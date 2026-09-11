"""
업종(service_name) 기준으로 자치구(district_name)별 창업 적합도 점수를 계산합니다.

가중치 (사용자와 합의된 기준):
- 수익성 (점포당 월매출)         : 35%
- 안정성 (개업률 - 폐업률)       : 35%
- 최근 추세 (성장 모멘텀)        : 15%
- 경쟁밀도 대비 시장 여유        : 15%
성별 매출 구성비는 점수에는 반영하지 않고, 타겟 적합도를 설명하기 위한
참고 정보로만 별도 제공합니다 (컨설팅 코멘트용).

데이터 품질 관련:
- 점수 계산에는 sales_data_type == 'actual'(실측) 데이터만 사용합니다.
  실측 데이터가 없는 자치구는 순위에서 제외합니다 (추정치로 순위를 매기면
  신뢰도가 떨어지기 때문입니다).
- 2021~2022년 분기는 코로나 영향으로 인한 이상치 가능성이 높아, "최근 추세"
  계산에서 완전히 제외합니다 (가중치를 낮추는 게 아니라 아예 배제).
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from models.district import CommercialDistrict

WEIGHTS = {
    "profitability": 0.35,   # 수익성
    "stability": 0.35,       # 안정성
    "trend": 0.15,           # 최근 추세
    "market_room": 0.15,     # 경쟁밀도 대비 시장 여유
}

# 이상치 가능성이 높아 "최근 추세" 계산에서 제외할 연도
TREND_EXCLUDED_YEARS = {2021, 2022}

# 추세를 의미 있게 계산하려면 최소 이만큼의 유효 분기(2021~2022 제외)가 필요함
MIN_QUARTERS_FOR_TREND = 8  # 최근 4개 + 그 이전 4개


def _format_quarter(year_quarter_code: int | None) -> str:
    if not year_quarter_code:
        return "알 수 없음"
    year, quarter = divmod(year_quarter_code, 10)
    return f"{year}년 {quarter}분기"


def _minmax_normalize(values: dict[str, float]) -> dict[str, float]:
    """딕셔너리 값들을 0~100 사이로 정규화. 값이 모두 같으면 중립값(50)으로 처리."""
    if not values:
        return {}
    vals = list(values.values())
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return {k: 50.0 for k in values}
    return {k: (v - lo) / (hi - lo) * 100 for k, v in values.items()}


@dataclass
class _DistrictSnapshot:
    district_name: str
    latest_row: CommercialDistrict
    profitability_raw: float          # 점포당 월매출
    stability_raw: float              # 개업률 - 폐업률
    market_room_raw: float            # 총 점포수 (낮을수록 여유 있음 -> 나중에 역산)
    trend_growth_ratio: float | None  # 최근4분기평균 / 이전4분기평균, 계산 불가하면 None


def _build_district_snapshot(district_name: str, rows: list[CommercialDistrict]) -> _DistrictSnapshot | None:
    """실측(actual) 데이터만 사용해 자치구 하나의 스냅샷을 만든다."""
    actual_rows = [r for r in rows if r.sales_data_type == "actual"]
    if not actual_rows:
        return None

    latest_row = max(actual_rows, key=lambda r: r.year_quarter_code)

    if not latest_row.total_store_count:
        return None  # 점포수가 없으면 점포당 매출 계산 불가 -> 순위 산정에서 제외

    profitability_raw = (latest_row.monthly_sales_amount or 0) / latest_row.total_store_count
    stability_raw = (latest_row.opening_rate or 0) - (latest_row.closing_rate or 0)
    market_room_raw = latest_row.total_store_count

    trend_growth_ratio = _calc_trend_growth_ratio(actual_rows)

    return _DistrictSnapshot(
        district_name=district_name,
        latest_row=latest_row,
        profitability_raw=profitability_raw,
        stability_raw=stability_raw,
        market_room_raw=market_room_raw,
        trend_growth_ratio=trend_growth_ratio,
    )


def _calc_trend_growth_ratio(actual_rows: list[CommercialDistrict]) -> float | None:
    """
    2021~2022년을 제외한 분기 중, 최근 4개 분기 평균 매출 / 그 이전 4개 분기 평균 매출.
    유효 분기가 충분치 않으면 None을 반환한다 (추세를 판단하지 않음).
    """
    valid_rows = [
        r for r in actual_rows
        if (r.year_quarter_code // 10) not in TREND_EXCLUDED_YEARS and r.monthly_sales_amount
    ]
    if len(valid_rows) < MIN_QUARTERS_FOR_TREND:
        return None

    valid_rows.sort(key=lambda r: r.year_quarter_code)  # 오래된 -> 최신 순
    recent_4 = valid_rows[-4:]
    prev_4 = valid_rows[-8:-4]

    prev_avg = sum(r.monthly_sales_amount for r in prev_4) / 4
    if prev_avg == 0:
        return None

    recent_avg = sum(r.monthly_sales_amount for r in recent_4) / 4
    return recent_avg / prev_avg


def rank_regions_for_category(
    db: Session,
    category: str,
    candidate_regions: list[str] | None = None,
    top_n: int = 5,
) -> dict:
    """
    특정 업종(category = store.service_name)에 대해 자치구별 창업 적합도 점수를 계산해
    상위 top_n개를 반환한다.

    candidate_regions를 지정하면 그 지역들 안에서만 순위를 매기고,
    지정하지 않으면 서울 전체 자치구를 대상으로 한다.
    """
    query = db.query(CommercialDistrict).filter(CommercialDistrict.service_name == category)
    if candidate_regions:
        query = query.filter(CommercialDistrict.district_name.in_(candidate_regions))

    rows_by_district: dict[str, list[CommercialDistrict]] = {}
    for row in query.all():
        rows_by_district.setdefault(row.district_name, []).append(row)

    snapshots = []
    for district_name, rows in rows_by_district.items():
        snap = _build_district_snapshot(district_name, rows)
        if snap:
            snapshots.append(snap)

    if not snapshots:
        return {
            "업종": category,
            "결과": [],
            "안내": "실측 데이터가 있는 자치구를 찾지 못해 순위를 계산할 수 없습니다.",
        }

    # 지표별로 정규화 (같은 업종 내 자치구 간 상대 비교)
    profitability_norm = _minmax_normalize({s.district_name: s.profitability_raw for s in snapshots})
    stability_norm = _minmax_normalize({s.district_name: s.stability_raw for s in snapshots})
    # 시장 여유: 점포수가 적을수록 여유 있는 것 -> 정규화 후 뒤집기(100 - x)
    market_room_norm_raw = _minmax_normalize({s.district_name: s.market_room_raw for s in snapshots})
    market_room_norm = {k: 100 - v for k, v in market_room_norm_raw.items()}

    trend_candidates = {s.district_name: s.trend_growth_ratio for s in snapshots if s.trend_growth_ratio is not None}
    trend_norm = _minmax_normalize(trend_candidates) if trend_candidates else {}

    results = []
    for s in snapshots:
        trend_score = trend_norm.get(s.district_name, 50.0)  # 계산 불가 시 중립값
        trend_available = s.district_name in trend_norm

        total_score = (
            profitability_norm[s.district_name] * WEIGHTS["profitability"]
            + stability_norm[s.district_name] * WEIGHTS["stability"]
            + trend_score * WEIGHTS["trend"]
            + market_room_norm[s.district_name] * WEIGHTS["market_room"]
        )

        male = s.latest_row.male_sales_amount or 0
        female = s.latest_row.female_sales_amount or 0
        gender_total = male + female
        gender_note = None
        if gender_total > 0:
            female_ratio = round(female / gender_total * 100, 1)
            male_ratio = round(100 - female_ratio, 1)
            gender_note = f"남성 {male_ratio}% / 여성 {female_ratio}%"

        results.append({
            "지역": s.district_name,
            "종합점수": round(total_score, 1),
            "기준분기": _format_quarter(s.latest_row.year_quarter_code),
            "수익성": {
                "점수": round(profitability_norm[s.district_name], 1),
                "점포당_월매출": f"{round(s.profitability_raw):,}원",
            },
            "안정성": {
                "점수": round(stability_norm[s.district_name], 1),
                "개업률-폐업률(%p)": round(s.stability_raw, 2),
            },
            "최근추세": {
                "점수": round(trend_score, 1) if trend_available else None,
                "성장률(%)": round((s.trend_growth_ratio - 1) * 100, 1) if s.trend_growth_ratio is not None else None,
                "비고": None if trend_available else "유효 분기 부족(2021~2022 제외 시)으로 중립 처리",
            },
            "시장여유": {
                "점수": round(market_room_norm[s.district_name], 1),
                "총점포수": s.latest_row.total_store_count,
            },
            "성별매출_참고": gender_note,
        })

    results.sort(key=lambda x: x["종합점수"], reverse=True)
    return {
        "업종": category,
        "가중치": {
            "수익성": "35%", "안정성": "35%", "최근추세": "15%", "시장여유": "15%",
        },
        "결과": results[:top_n],
    }