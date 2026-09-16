"""
analysis_inference.py
------------------------
Page 2 "매출 예상액" 실시간 예측 모듈.

Page 1(inference.py)과 구조는 비슷하지만 2가지가 다르다:
    1. CSV를 직접 읽지 않고, models/district.py의 CommercialDistrict ORM으로
       DB(store 테이블)에서 실시간 조회한다. (팀원이 만들어둔 모델 재사용)
    2. 원본 데이터는 "그 지역+업종 전체 점포 합산 매출"인데, 사용자가 묻는 건
       "내 가게 하나"의 예상 매출이므로, 합산 매출을 전체 점포수로 나눠서
       "점포당 평균 매출"로 변환한 뒤에 보여준다.

파일 위치: server/router/analysis_inference.py
(직접 실행하는 파일이 아니라, analysis.py가 import해서 쓰는 헬퍼 모듈입니다.)
"""

import os
import joblib
import pandas as pd
from sqlalchemy.orm import Session

from models.district import CommercialDistrict
from core.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "ml", "page2", "revenue_models.pkl")

N_RECENT_QUARTERS = 5   # 화면에 보여줄 "실측" 분기 개수
N_FORECAST_QUARTERS = 4  # 화면에 보여줄 "예측" 분기 개수

_revenue_models = None  # 서버 시작 후 한 번만 로드해서 재사용 (Page1과 동일한 캐싱 패턴)


def load_revenue_models():
    global _revenue_models
    if _revenue_models is None:
        bundle = joblib.load(MODEL_PATH)
        _revenue_models = bundle["models"]
        logger.info("Page2 모델 %d개 조합 로드 완료", len(_revenue_models))
    return _revenue_models


def format_quarter_label(year_quarter_code: int) -> str:
    """20254 -> '25.4' (프론트 QuarterPoint.quarter 형식과 동일)"""
    year, quarter = divmod(year_quarter_code, 10)
    return f"{year % 100}.{quarter}"


def format_manwon(amount_in_won: float) -> str:
    """82000000(원) -> '8,200만원'"""
    manwon = round(amount_in_won / 10000)
    return f"{manwon:,}만원"


def get_history(db: Session, district_code: str, service_code: str):
    """DB(store 테이블)에서 해당 지역+업종의 전체 분기 이력을 시간순으로 조회.
    CommercialDistrict ORM 모델을 통해 조회하므로, load_data.py로 적재된
    실데이터를 CSV 없이 바로 DB에서 가져온다.

    mock(추정치) 분기는 제외한다 - train_model.py도 동일하게 actual 데이터만
    학습에 썼으므로, 화면에 "실측"이라고 보여주는 데이터도 진짜 실측이어야
    앞뒤가 맞는다. (그렇지 않으면 100% mock인 조합이 마치 실제 매출이 있는
    것처럼 차트에 나오는 문제가 생김 - 실제로 예술품 카테고리에서 발견됨)"""
    rows = (
        db.query(CommercialDistrict)
        .filter(
            CommercialDistrict.district_code == str(district_code),
            CommercialDistrict.service_code == service_code,
            CommercialDistrict.sales_data_type == "actual",
        )
        .order_by(CommercialDistrict.year_quarter_code)
        .all()
    )
    return rows


def build_analysis_result(db: Session, district_code: str, service_code: str, target_sales_manwon: int) -> dict | None:
    """AnalysisResponse 형태(averageSales/vsTarget/predictedSales/targetAchieveRate/insight/quarters)로 조립."""
    history = get_history(db, district_code, service_code)
    if len(history) < 2:
        return None  # 데이터가 너무 적으면 분석 불가

    revenue_models = load_revenue_models()
    model_key = (int(district_code), service_code)
    model_entry = revenue_models.get(model_key)
    if model_entry is None:
        return None  # 이 조합은 학습 데이터가 부족해서 모델이 아예 없는 경우

    model = model_entry["model"]
    last_trend = model_entry["last_trend"]

    # ── 점포당 평균 매출로 변환 (합산 매출 ÷ 그 분기 전체 점포수) ──
    per_store_history = []
    for row in history:
        store_count = row.total_store_count or 1  # 0으로 나누기 방지
        per_store_revenue = (row.monthly_sales_amount or 0) / store_count
        per_store_history.append({
            "quarter_code": row.year_quarter_code,
            "per_store_revenue": per_store_revenue,
        })

    latest_store_count = history[-1].total_store_count or 1

    # ── 최근 N_RECENT_QUARTERS개 분기를 "실측" 데이터로 화면에 표시 ──
    recent = per_store_history[-N_RECENT_QUARTERS:]
    quarters = [
        {
            "quarter": format_quarter_label(q["quarter_code"]),
            "actual": round(q["per_store_revenue"] / 10000),  # 만원 단위 정수
            "predicted": None,
            "target": target_sales_manwon,
        }
        for q in recent
    ]

    # ── 다음 N_FORECAST_QUARTERS개 분기 예측 (모델은 "합산 매출"을 예측하므로,
    #     최근 점포수로 다시 나눠서 "점포당 평균"으로 환산) ──
    is_q2 = is_q3 = is_q4 = 0
    last_quarter_code = history[-1].year_quarter_code
    year, quarter_num = divmod(last_quarter_code, 10)

    predicted_manwon_list = []
    for i in range(1, N_FORECAST_QUARTERS + 1):
        future_trend = last_trend + i
        future_quarter_num = ((quarter_num - 1 + i) % 4) + 1
        future_year = year + (quarter_num - 1 + i) // 4

        is_q2 = 1 if future_quarter_num == 2 else 0
        is_q3 = 1 if future_quarter_num == 3 else 0
        is_q4 = 1 if future_quarter_num == 4 else 0

        X_future = pd.DataFrame([[future_trend, is_q2, is_q3, is_q4]],
                                 columns=["trend", "is_q2", "is_q3", "is_q4"])
        predicted_aggregate = model.predict(X_future)[0]
        predicted_per_store = predicted_aggregate / latest_store_count
        predicted_manwon = round(predicted_per_store / 10000)
        predicted_manwon_list.append(predicted_manwon)

        future_quarter_code = future_year * 10 + future_quarter_num
        quarters.append({
            "quarter": format_quarter_label(future_quarter_code),
            "actual": None,
            "predicted": predicted_manwon,
            "target": target_sales_manwon,
        })

    # ── 목표 달성 확률: RandomForest 안의 개별 트리들 예측값 분포 활용 ──
    # (Page2 설계 때 검증한 방식 - 별도 통계 모델 없이 트리 앙상블 자체로 확률 추정)
    first_future_X = pd.DataFrame(
        [[last_trend + 1, 1 if quarter_num % 4 + 1 == 2 else 0, 0, 0]],
        columns=["trend", "is_q2", "is_q3", "is_q4"],
    )
    tree_predictions_won = [tree.predict(first_future_X)[0] for tree in model.estimators_]
    tree_predictions_per_store_manwon = [
        (pred / latest_store_count) / 10000 for pred in tree_predictions_won
    ]
    n_trees_over_target = sum(1 for p in tree_predictions_per_store_manwon if p >= target_sales_manwon)
    target_achieve_rate = round(n_trees_over_target / len(tree_predictions_per_store_manwon) * 100)

    # ── 요약 통계 ──
    average_sales_manwon = round(sum(q["actual"] for q in quarters if q["actual"] is not None)
                                  / max(1, sum(1 for q in quarters if q["actual"] is not None)))
    next_predicted_manwon = predicted_manwon_list[0]
    vs_target_pct = round((average_sales_manwon - target_sales_manwon) / target_sales_manwon * 100)

    insight = (
        f"최근 {len(recent)}개 분기 점포당 평균 매출은 {average_sales_manwon:,}만원이며, "
        f"이 지역/업종 전체 {latest_store_count}개 점포 데이터를 기반으로 산출했습니다. "
        f"다음 분기 예상 매출은 {next_predicted_manwon:,}만원으로, "
        f"목표 매출 {target_sales_manwon:,}만원 달성 가능성은 {target_achieve_rate}%입니다. "
        f"평균은 이미 자리잡은 기존 점포까지 포함된 수치이므로, 신규 창업 초기에는 "
        f"이보다 낮을 수 있다는 점을 참고해주세요."
    )

    return {
        "averageSales": format_manwon(average_sales_manwon * 10000),
        "vsTarget": f"{vs_target_pct:+d}%",
        "predictedSales": format_manwon(next_predicted_manwon * 10000),
        "targetAchieveRate": f"{target_achieve_rate}%",
        "insight": insight,
        "quarters": quarters,
    }