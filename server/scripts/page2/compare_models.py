"""
compare_models.py (page2)
-------------------------------
Page 2-2 "매출 예상액" 모델 비교.

Page 1과 다른 백테스트 방식: 지역x업종 조합 하나마다 개별로 회귀를 학습시키고
(그 조합의 과거 15개 분기로 학습, 최근 4개 분기로 검증), 이를 2,000개가 넘는
모든 조합에 대해 반복한 뒤 평균을 내서 "어떤 모델이 전반적으로 제일 정확한지" 비교.

비교 대상:
    - LinearRegression (OLS와 동일한 결과, 팀에서 원래 채택하려던 방식)
    - Ridge (정규화를 추가한 선형회귀 - 과적합 방지 효과 확인용)
    - RandomForestRegressor (얕은 깊이 - 데이터가 적어도 되는지 확인용)
    - GradientBoostingRegressor (얕은 깊이)

지표: MAPE(메인), RMSE/R²(참고) - 매출 규모가 업종마다 다르므로 %기반 지표 우선.

실행 위치: server/scripts/page2/compare_models.py
결과물: server/ml/page2/model_comparison_results.csv
"""

import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, ElasticNet
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score

from feature_engineering import prepare_all_series, FEATURE_COLS, TARGET_COL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "..", "ml", "page2")
RESULTS_PATH = os.path.join(MODEL_DIR, "model_comparison_results.csv")

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("[info] xgboost 미설치 - 비교 대상에서 제외합니다.")

try:
    from lightgbm import LGBMRegressor
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False
    print("[info] lightgbm 미설치 - 비교 대상에서 제외합니다.")


def get_candidate_models():
    # 조합당 학습 데이터가 15개 안팎으로 매우 적으므로, 모든 모델을 일부러
    # 얕고 단순하게 설정함 (복잡한 모델은 이런 소규모 데이터에서 과적합 위험 큼)
    models = {
        "LinearRegression(OLS)": LinearRegression(),
        "Ridge": Ridge(alpha=1.0, random_state=42),
        "ElasticNet": ElasticNet(alpha=0.5, l1_ratio=0.5, random_state=42),
        "RandomForest(얕음)": RandomForestRegressor(
            n_estimators=50, max_depth=2, min_samples_leaf=1, random_state=42, n_jobs=-1
        ),
        "ExtraTrees(얕음)": ExtraTreesRegressor(
            n_estimators=50, max_depth=2, min_samples_leaf=1, random_state=42, n_jobs=-1
        ),
        "GradientBoosting(얕음)": GradientBoostingRegressor(
            n_estimators=30, max_depth=2, learning_rate=0.1, random_state=42
        ),
        "HistGradientBoosting(얕음)": HistGradientBoostingRegressor(
            max_depth=2, max_iter=30, learning_rate=0.1, random_state=42
        ),
    }
    if HAS_XGB:
        models["XGBoost(얕음)"] = XGBRegressor(
            n_estimators=30, max_depth=2, learning_rate=0.1, random_state=42, n_jobs=-1
        )
    if HAS_LGBM:
        models["LightGBM(얕음)"] = LGBMRegressor(
            n_estimators=30, max_depth=2, learning_rate=0.1, random_state=42, n_jobs=-1, verbose=-1,
            min_child_samples=3,  # 데이터가 적으니 leaf 최소 샘플 조건도 낮춰줌
        )
    return models


def backtest_all_series():
    series_list = prepare_all_series()
    print(f"[data] 백테스트 대상 조합 수: {len(series_list)}개")

    candidates = get_candidate_models()
    per_series_results = {name: [] for name in candidates}

    for district_code, service_code, train, test in series_list:
        X_train, y_train = train[FEATURE_COLS], train[TARGET_COL]
        X_test, y_test = test[FEATURE_COLS], test[TARGET_COL]

        # 타겟이 0이면 MAPE 계산이 불가능(분모 0)하므로 그런 조합은 건너뜀
        if (y_test == 0).any() or (y_train == 0).all():
            continue

        for name, model in candidates.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                mape = mean_absolute_percentage_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred) if len(y_test) > 1 else np.nan

                per_series_results[name].append({
                    "district_code": district_code,
                    "service_code": service_code,
                    "mape": mape,
                    "rmse": rmse,
                    "r2": r2,
                })
            except Exception:
                continue

    return per_series_results


def summarize(per_series_results):
    rows = []
    for name, results in per_series_results.items():
        df = pd.DataFrame(results)
        rows.append({
            "model": name,
            "n_series": len(df),
            "mape_median": df["mape"].median(),
            "pct_under_50": (df["mape"] < 0.5).mean() * 100,
            "mape_mean": df["mape"].mean(),  # 참고용 (극단치에 왜곡되기 쉬우니 median을 우선 신뢰)
            "rmse_mean": df["rmse"].mean(),
            "r2_mean": df["r2"].mean(),
        })
    # 평균이 아니라 중앙값 기준으로 정렬 (극단치 왜곡 방지 - 이전 튜닝에서 확인된 문제)
    summary = pd.DataFrame(rows).sort_values("mape_median").reset_index(drop=True)
    return summary


def run():
    per_series_results = backtest_all_series()
    summary = summarize(per_series_results)

    print("\n=== Page 2-2 모델 비교 결과 (중앙값 MAPE 기준 정렬) ===")
    print(summary.to_string(index=False))

    os.makedirs(MODEL_DIR, exist_ok=True)
    summary.to_csv(RESULTS_PATH, index=False, encoding="utf-8-sig")
    print(f"\n[save] 결과 저장 -> {RESULTS_PATH}")

    return summary


if __name__ == "__main__":
    run()
