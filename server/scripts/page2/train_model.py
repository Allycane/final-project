"""
train_model.py (page2)
----------------------------
Page 2-2 "매출 예상액" 최종 모델 학습.

Page 1과 다른 구조: 지역+업종 조합마다 별도의 작은 RandomForest를 학습시켜서,
전체를 하나의 딕셔너리(조합 -> 모델)로 묶어 저장한다. (조합 개수만큼 모델이 생김)

예측 시:
    - 점 예측: 100개 트리 예측의 평균
    - 목표 달성 확률: 100개 트리 예측값 중 목표 이상인 비율

실행 위치: server/scripts/page2/train_model.py
결과물: server/ml/page2/revenue_models.pkl
"""

import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error

from feature_engineering import load_data, filter_actual_only, add_trend_and_season, get_eligible_groups, FEATURE_COLS, TARGET_COL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "..", "ml", "page2")
MODEL_PATH = os.path.join(MODEL_DIR, "revenue_models.pkl")


def train():
    df = load_data()
    df = filter_actual_only(df)
    df = add_trend_and_season(df)
    df = get_eligible_groups(df)

    models = {}
    metrics = []

    for (district_code, service_code), group in df.groupby(["district_code", "service_code"]):
        group = group.sort_values("year_quarter_code").reset_index(drop=True)

        X = group[FEATURE_COLS]
        y = group[TARGET_COL]

        # 최종 서비스용 모델은 검증 안 남기고 가진 데이터 전부로 학습
        # (하이퍼파라미터/방법론 검증은 compare_models.py 백테스트에서 이미 끝냄)
        model = RandomForestRegressor(
            n_estimators=100, max_depth=3, min_samples_leaf=1,
            random_state=42, n_jobs=-1,
        )
        model.fit(X, y)

        models[(district_code, service_code)] = {
            "model": model,
            "last_trend": int(X["trend"].max()),
            "service_name": group["service_name"].iloc[-1],
        }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(
        {
            "models": models,
            "feature_cols": FEATURE_COLS,
        },
        MODEL_PATH,
    )
    print(f"[save] {len(models)}개 조합의 모델 저장 완료 -> {MODEL_PATH}")


if __name__ == "__main__":
    train()