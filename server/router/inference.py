"""
inference.py
--------------
Page 1 "업종 추천" 실시간 예측 모듈.

학습 스크립트(server/scripts/page1/*)와 똑같은 피처 엔지니어링 로직을 "최신 분기"에
적용해서, 실제 서비스 요청이 들어왔을 때 모델 예측 + 추천/비추천/참고 랭킹까지 계산한다.

핵심 흐름:
    1. 서버 시작 시 한 번만 recommendation_model.pkl 로드 (매 요청마다 로드하면 느림)
    2. store 테이블(DB)에서 최신 분기(예: 26-1) 데이터 로드 + 피처 계산
       (전분기 대비 성장률 계산을 위해 그 이전 분기 데이터도 함께 필요)
    3. 사용자가 고른 지역(district_code) + 후보 업종(service_code 목록) 대상으로
       모델이 "다음 분기 상위 25%" 확률을 예측
    4. 그 확률 기준으로 정렬해서 상위 30%=추천, 하위 30%=비추천, 그 외 상위 하나=참고

파일 위치: server/router/inference.py
(직접 실행하는 파일이 아니라, recommend.py가 import해서 쓰는 헬퍼 모듈입니다.
 python inference.py 처럼 따로 실행하실 필요 없어요.)

※ 데이터 소스 변경 이력 ※
원래는 seoul_store.csv 파일을 읽었지만, 실제 서비스 DB에 이미 동일한 데이터가
store 테이블(models/district.py의 CommercialDistrict)로 들어가 있으므로 CSV 대신
DB에서 직접 조회하도록 변경함. 모델(recommendation_model.pkl) 자체는 그대로
파일에서 로드한다 - 이건 미리 학습해둔 모델 바이너리라 DB와 무관함.
"""

import os
import numpy as np
import pandas as pd
import joblib
from sqlalchemy import select

from database.connection import engine
from models.district import CommercialDistrict as StoreModel
from core.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "ml", "page1", "recommendation_model.pkl")

FEATURE_COLS = [
    "sales_growth_rate", "net_store_change_rate", "total_store_count",
    "opening_rate", "closing_rate", "growth_pct_rank", "is_bottom25_growth",
]
CATEGORICAL_COLS = ["service_category", "district_code"]

# no_sales_data의 한글 "reason" 문구 -> 프론트엔드가 안정적으로 분기 처리할 수 있는
# 코드값 매핑. reason 문구 자체는 나중에 바뀔 수 있어도 reasonCode는 고정.
#   - "mock": sales_data_type이 실제로 mock(추정치)이라 제외된 경우
#   - "volatile": 실측 데이터지만 변동성이 너무 커서 제외된 경우 (mock과는 다른 사유)
REASON_TO_CODE = {
    "데이터 부족": "mock",
    "매출 변동성 과다": "volatile",
}

_model_bundle = None      # 서버 시작 시 한 번만 로드해서 캐시
_latest_features_df = None   # 최신 분기 피처 계산 결과 캐시 (품질 검증 통과한 것만)
_excluded_features_df = None  # 품질 문제로 제외된 것들 (이유 포함) 캐시
_code_to_name = None      # service_code -> service_name 매핑 (mock 여부 무관하게 이름 표시용)


def _load_store_dataframe() -> pd.DataFrame:
    """store 테이블에서 피처 계산에 필요한 컬럼만 조회해서 DataFrame으로 반환."""
    query = select(
        StoreModel.district_code,
        StoreModel.service_code,
        StoreModel.service_name,
        StoreModel.year_quarter_code,
        StoreModel.monthly_sales_amount,
        StoreModel.opening_store_count,
        StoreModel.closing_store_count,
        StoreModel.total_store_count,
        StoreModel.opening_rate,
        StoreModel.closing_rate,
        StoreModel.sales_data_type,
    )
    df = pd.read_sql(query, engine)

    # DB에는 district_code가 문자열(String)로 저장돼 있는데, 이후 로직에서
    # district_code == int(요청으로 들어온 자치구 코드) 비교를 하므로 int로 변환.
    # (서울 자치구 코드는 전부 "11xxx" 5자리라 앞자리 0으로 인한 손실 없음)
    df["district_code"] = df["district_code"].astype(int)
    return df


def get_code_to_name():
    """mock으로 걸러진 업종도 이름은 보여줘야 하므로, service_code -> service_name
    매핑을 store 테이블에서 조회해 캐시."""
    global _code_to_name
    if _code_to_name is None:
        query = select(StoreModel.service_code, StoreModel.service_name).distinct()
        rows = pd.read_sql(query, engine)
        _code_to_name = dict(zip(rows["service_code"], rows["service_name"]))
    return _code_to_name


def load_model_bundle():
    """recommendation_model.pkl 로드 (모델 + 인코더 + 스케일러 등 한 번에).
    FastAPI 앱 시작 시(main.py의 startup 이벤트) 한 번 호출해서 캐시해두는 용도."""
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(MODEL_PATH)
        logger.info("모델 로드 완료: %s", _model_bundle.get("model_name", "unknown"))
    return _model_bundle

def preload():
    """서버 시작 시 호출: 모델 + 최신 분기 피처를 미리 로드/계산해서 캐시."""
    load_model_bundle()
    _compute_latest_quarter_features()


def _compute_latest_quarter_features():
    """store 테이블 전체를 읽어서, 학습 때와 동일한 방식으로 피처를 계산한 뒤
    '가장 최근 분기'(예: 26-1, 라벨은 없지만 피처는 있는 분기) 행만 추려서 반환.
    이 최근 분기 데이터가 바로 실시간 추천에 쓰이는 입력값이다."""
    global _latest_features_df, _excluded_features_df
    if _latest_features_df is not None:
        return _latest_features_df

    df = _load_store_dataframe()
    df["service_category"] = df["service_code"].str.extract(r"(CS\d)")
    df = df[df["service_category"].isin(["CS1", "CS2", "CS3"])].copy()

    df = df.sort_values(["district_code", "service_code", "year_quarter_code"]).copy()
    grp = df.groupby(["district_code", "service_code"], group_keys=False)

    df["prev_sales"] = grp["monthly_sales_amount"].shift(1)
    df["sales_growth_rate_1q"] = (df["monthly_sales_amount"] - df["prev_sales"]) / df["prev_sales"]

    # "2년(직전 8개 분기)" 추세 기반 - feature_engineering.py와 반드시 동일하게 유지
    WINDOW_QUARTERS = 8
    df["sales_growth_rate"] = grp["sales_growth_rate_1q"].transform(
        lambda s: s.rolling(WINDOW_QUARTERS - 1).mean()
    )
    for i in range(1, WINDOW_QUARTERS):
        df[f"prev{i}_sales_data_type"] = grp["sales_data_type"].shift(i)

    df["net_store_change_rate"] = (
        (df["opening_store_count"] - df["closing_store_count"])
        / df["total_store_count"].replace(0, np.nan)
    )
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["sales_growth_rate", "net_store_change_rate"])

    df["growth_pct_rank"] = (
        df.groupby(["service_category", "year_quarter_code"])["sales_growth_rate"]
        .transform(lambda g: g.rank(pct=True))
    )
    df["is_bottom25_growth"] = (df["growth_pct_rank"] <= 0.25).astype(int)

    latest_quarter = df["year_quarter_code"].max()
    latest_df = df[df["year_quarter_code"] == latest_quarter].copy()

    # ── 데이터 품질 필터 1: mock(추정치) 제외 ──
    # 2년 추세 계산에 쓰인 8개 분기 중 하나라도 mock이면 추세 자체가 진짜 시장
    # 신호가 아니므로 추천 후보에서 제외.
    before_mock = len(latest_df)
    latest_df["exclusion_reason"] = None
    is_mock = latest_df["sales_data_type"] != "actual"
    for i in range(1, WINDOW_QUARTERS):
        is_mock = is_mock | (latest_df[f"prev{i}_sales_data_type"] != "actual")
    latest_df.loc[is_mock, "exclusion_reason"] = "데이터 부족"

    # ── 데이터 품질 필터 2: 실측이어도 변동성이 너무 큰 업종 제외 ──
    # 부동산중개업처럼 매출 자체가 원래 들쭉날쭉한(계약 건수 따라 요동치는) 업종은
    # mock은 아니지만 -50%/+83% 같은 극단적 수치로 신뢰하기 어려운 결과를 만듦.
    # 성장률 절대값 50% 초과 시 "변동성 과다"로 제외 (실측 데이터의 약 6%만 해당,
    # 대다수 업종에는 영향 없음).
    VOLATILITY_THRESHOLD = 0.5
    is_volatile = (~is_mock) & (latest_df["sales_growth_rate"].abs() >= VOLATILITY_THRESHOLD)
    latest_df.loc[is_volatile, "exclusion_reason"] = "매출 변동성 과다"

    excluded_df = latest_df[latest_df["exclusion_reason"].notna()].copy()
    latest_df = latest_df[latest_df["exclusion_reason"].isna()].copy()

    logger.info(
        "데이터 품질 필터링: %d건 -> %d건 (데이터 부족 %d건, 변동성 과다 %d건 제외)",
        before_mock, len(latest_df), is_mock.sum(), is_volatile.sum(),
    )

    _latest_features_df = latest_df
    _excluded_features_df = excluded_df
    logger.info("최신 분기(%s) 피처 계산 완료: %d건", latest_quarter, len(latest_df))
    return latest_df


def _encode_features(df: pd.DataFrame, encoders: dict) -> pd.DataFrame:
    """학습 때 만든 인코더(LabelEncoder)를 그대로 재사용해서 인코딩.
    학습 때 못 본 새 값이 있으면 -1로 처리."""
    df = df.copy()
    encoded_cols = []
    for col in CATEGORICAL_COLS:
        le = encoders[col]
        df[f"{col}_enc"] = df[col].astype(str).map(
            lambda v: le.transform([v])[0] if v in le.classes_ else -1
        )
        encoded_cols.append(f"{col}_enc")
    return df[FEATURE_COLS + encoded_cols]


def predict_growth_probability(district_code: int, service_codes: list[str]) -> pd.DataFrame:
    """지정한 지역 + 후보 업종들에 대해 '다음 분기 상위 25% 진입 확률'을 계산.
    반환: service_code, service_name, sales_growth_rate, net_store_change_rate,
          growth_probability 컬럼을 가진 DataFrame (확률 내림차순 정렬)."""
    bundle = load_model_bundle()
    model = bundle["model"]
    scaler = bundle.get("scaler")
    encoders = bundle["encoders"]

    latest_df = _compute_latest_quarter_features()

    candidates = latest_df[
        (latest_df["district_code"] == district_code)
        & (latest_df["service_code"].isin(service_codes))
    ].copy()

    if candidates.empty:
        return candidates

    X = _encode_features(candidates, encoders)
    X_use = scaler.transform(X) if scaler is not None else X

    candidates["growth_probability"] = model.predict_proba(X_use)[:, 1]

    return candidates[[
        "service_code", "service_name", "sales_growth_rate",
        "net_store_change_rate", "growth_probability",
    ]].sort_values("growth_probability", ascending=False).reset_index(drop=True)


def _not_recommended_badge(row) -> str:
    """
    비추천 업종의 배지는 매출/점포수 증감 '방향'을 참고하되, '성장'이나
    '동반성장'처럼 긍정적으로 들리는 단어는 절대 쓰지 않는다. 이 목록에 있는
    업종은 이미 AI 모델이 '다음 분기 성장 확률 하위 30%'로 판단해서 비추천으로
    분류한 것이므로, 이번 분기 매출이 우연히 소폭 올랐더라도 배지는 항상
    "이 업종을 선택하면 불리하다"는 방향으로 명확하게 표시한다.

    (예전엔 점포수만 보고 배지를 정해서, 매출이 +34.9%인데도 '쇠퇴'로 잘못
    표시되는 버그가 있었음 - 반드시 두 축을 함께 판단해야 함)
    """
    growing_sales = row["sales_growth_rate"] >= 0
    growing_stores = row["net_store_change_rate"] >= 0

    if not growing_sales and growing_stores:
        return "공급과잉"       # 매출은 주는데 점포는 늘어남 - 경쟁 심화
    if not growing_sales and not growing_stores:
        return "쇠퇴"          # 매출도 점포도 둘 다 감소
    # 매출/점포 지표상으로는 늘고 있는 것처럼 보여도, 모델이 하위 30%로
    # 판단해 비추천에 포함된 항목이므로 '성장' 계열 표현은 쓰지 않는다.
    return "성장 둔화 우려"


def _describe_trend(row) -> str:
    """성장률/순증감률 수치를 자연스러운 문장으로 풀어주는 헬퍼 (배지와는 무관)."""
    growth_pct = row["sales_growth_rate"] * 100
    store_pct = row["net_store_change_rate"] * 100
    prob_pct = row["growth_probability"] * 100
    return (f"매출 {growth_pct:+.1f}%, 점포수 {store_pct:+.1f}% 추세이며, "
            f"다음 분기에도 잘될 가능성 {prob_pct:.0f}% 입니다.")


def build_recommendation_result(district_code: int, primary_codes: list[str], reference_codes: list[str] = None) -> dict:
    """POST /api/recommendation 응답 형태(recommended/notRecommended/reference/noSalesData)로 최종 조립.

    두 개의 서로 다른 후보군을 따로 처리한다:
        - primary_codes (사용자가 실제로 체크한 항목들): 이 안에서 순위를 매겨
          1등 = recommended, 하위 30% = notRecommended
        - reference_codes (사용자가 체크하지 않은 나머지 항목들): 이 안에서
          1등만 뽑아서 "선택 안 했지만 참고할 업종"으로 제공

    체크한 항목(primary_codes) 중 실측 매출 데이터가 없어서(mock만 있어서)
    비교 대상에서 아예 빠진 것들은 noSalesData로 별도 반환한다. 조용히 사라지게
    하지 않고, "이 업종들은 데이터가 부족해 비교에서 제외됐다"는 걸 사용자에게
    투명하게 보여주기 위함. reasonCode로 "mock"(추정치라 제외)과 "volatile"
    (실측이지만 변동성 과다로 제외)를 구분해서, 프론트엔드가 "mock 데이터 때문에
    제외된 것"만 따로 강조해서 보여줄 수 있게 한다.

    배지는 quadrant(매출/점포수 증감 부호)를 정확히 반영한다. 단, recommended만
    예외적으로 매출이 실제로 마이너스여도 "성장"이라 부르지 않고 "반등 기대"로
    구분해서, "추천인데 마이너스인데 성장?" 같은 모순을 방지한다.
    """
    ranked = predict_growth_probability(district_code, primary_codes)

    # 체크한 것 중 데이터 품질 문제로 비교 대상에서 빠진 코드들 (조용히 사라지지
    # 않게, 정확한 사유와 함께 별도 표시)
    code_to_name = get_code_to_name()
    excluded_lookup = {}
    if _excluded_features_df is not None:
        relevant_excluded = _excluded_features_df[
            (_excluded_features_df["district_code"] == district_code)
            & (_excluded_features_df["service_code"].isin(primary_codes))
        ]
        excluded_lookup = dict(zip(relevant_excluded["service_code"], relevant_excluded["exclusion_reason"]))

    available_codes = set(ranked["service_code"]) if not ranked.empty else set()
    no_data_codes = sorted(set(primary_codes) - available_codes)
    no_sales_data = [
        {
            "name": code_to_name.get(code, code),
            "reason": excluded_lookup.get(code, "데이터 부족"),
            "reasonCode": REASON_TO_CODE.get(excluded_lookup.get(code, "데이터 부족"), "unknown"),
        }
        for code in no_data_codes
    ]

    if ranked.empty:
        return {"recommended": None, "notRecommended": [], "reference": [], "noSalesData": no_sales_data}

    n = len(ranked)
    bottom_cut = max(1, int(np.ceil(n * 0.3)))

    top_row = ranked.iloc[0]
    bottom_pool = ranked.iloc[-bottom_cut:] if n > 1 else ranked.iloc[0:0]

    recommended_badge = "성장" if top_row["sales_growth_rate"] >= 0 else "반등 기대"

    recommended = {
        "name": top_row["service_name"],
        "badge": recommended_badge,
        "description": _describe_trend(top_row),
    }

    not_recommended = []
    for _, row in bottom_pool.iterrows():
        not_recommended.append({
            "name": row["service_name"],
            "badge": _not_recommended_badge(row),
            "description": _describe_trend(row),
        })

    # ── 참고: 체크 안 한 항목들 중 1등만 별도로 뽑음 (완전히 다른 후보군) ──
    # 배지는 quadrant와 무관하게 항상 "참고"로 고정한다. 추천/비추천과는 다른
    # 성격의 항목(사용자가 아예 선택하지 않은 업종 중 1등)이므로, '성장'이나
    # '동반성장'처럼 추천 항목과 헷갈릴 수 있는 표현은 쓰지 않는다.
    reference = []
    if reference_codes:
        ref_ranked = predict_growth_probability(district_code, reference_codes)
        if not ref_ranked.empty:
            ref_row = ref_ranked.iloc[0]
            reference.append({
                "name": ref_row["service_name"],
                "badge": "참고",
                "description": _describe_trend(ref_row),
            })

    return {
        "recommended": recommended,
        "notRecommended": not_recommended,
        "reference": reference,
        "noSalesData": no_sales_data,
    }