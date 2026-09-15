"""
compare_hyperparameters.py (page2)
-------------------------------------
Page 2 "매출 예상액" 하이퍼파라미터 비교.

Page 1과 다른 이유:
    Page 1은 모델이 1개라 그 안에서 학습/검증을 나눠 500개 조합을 시도할 수 있었다.
    Page 2는 모델이 조합마다(2,488개) 따로 있고 각 모델의 학습 데이터가 15개 안팎
    으로 너무 적어서, 개별 모델 안에서 파라미터를 튜닝하면 우연에 좌우되기 쉽다.

    대신: 파라미터 조합 하나를 고정한 뒤, 그 설정 그대로 2,488개 조합 전체에
    적용해 평균 성능(MAPE)을 본다. 조합 개수 자체가 이미 크기 때문에,
    "이 설정이 전체적으로 얼마나 잘 맞는지"를 충분히 신뢰할 수 있게 비교 가능.

실행 위치: server/scripts/page2/compare_hyperparameters.py
결과물: server/ml/page2/hyperparameter_comparison_results.csv
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error

from feature_engineering import prepare_all_series, FEATURE_COLS, TARGET_COL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "..", "ml", "page2")
RESULTS_PATH = os.path.join(MODEL_DIR, "hyperparameter_comparison_results.csv")

# 시도해볼 RandomForest 설정들 (데이터가 조합당 15개 안팎으로 적으므로,
# 너무 깊거나 트리가 너무 많은 설정은 오히려 과적합 위험이 큼 - 그래도 실제로
# 확인해보기 위해 얕은 것부터 좀 더 복잡한 것까지 폭넓게 시도)
CANDIDATE_CONFIGS = [
    {"n_estimators": 50,  "max_depth": 2, "min_samples_leaf": 1},
    {"n_estimators": 50,  "max_depth": 3, "min_samples_leaf": 1},
    {"n_estimators": 50,  "max_depth": 3, "min_samples_leaf": 2},
    {"n_estimators": 100, "max_depth": 2, "min_samples_leaf": 1},
    {"n_estimators": 100, "max_depth": 3, "min_samples_leaf": 1},
    {"n_estimators": 100, "max_depth": 3, "min_samples_leaf": 2},
    {"n_estimators": 100, "max_depth": 4, "min_samples_leaf": 2},
    {"n_estimators": 100, "max_depth": 4, "min_samples_leaf": 3},
    {"n_estimators": 100, "max_depth": 5, "min_samples_leaf": 3},
    {"n_estimators": 200, "max_depth": 3, "min_samples_leaf": 2},
    {"n_estimators": 200, "max_depth": 4, "min_samples_leaf": 3},
    {"n_estimators": 200, "max_depth": 5, "min_samples_leaf": 5},
]


def evaluate_config(config, series_list):
    """이 설정 그대로 2,488개 조합 전체에 적용해서 MAPE 리스트 반환."""
    mapes = []
    for district_code, service_code, train, test in series_list:
        X_train, y_train = train[FEATURE_COLS], train[TARGET_COL]
        X_test, y_test = test[FEATURE_COLS], test[TARGET_COL]

        if (y_test == 0).any() or (y_train == 0).all():
            continue

        model = RandomForestRegressor(random_state=42, n_jobs=-1, **config)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mapes.append(mean_absolute_percentage_error(y_test, y_pred))

    return mapes


def run():
    series_list = prepare_all_series()
    print(f"[data] 비교 대상 조합 수: {len(series_list)}개")
    print(f"[configs] 시도할 설정 수: {len(CANDIDATE_CONFIGS)}개\n")

    rows = []
    for i, config in enumerate(CANDIDATE_CONFIGS, 1):
        print(f"[{i}/{len(CANDIDATE_CONFIGS)}] {config} 평가 중...")
        mapes = evaluate_config(config, series_list)
        arr = np.array(mapes)

        row = {
            **config,
            "n_series": len(arr),
            "mape_median": np.median(arr),
            "mape_mean_trimmed": np.mean(arr[arr < np.percentile(arr, 95)]),  # 극단치 제외 평균
            "pct_under_50": (arr < 0.5).mean() * 100,
        }
        rows.append(row)
        print(f"  -> 중앙값 MAPE={row['mape_median']*100:.1f}%  "
              f"50%이하비율={row['pct_under_50']:.1f}%")

    results_df = pd.DataFrame(rows).sort_values("mape_median").reset_index(drop=True)

    print("\n=== 전체 비교 결과 (중앙값 MAPE 기준 정렬) ===")
    print(results_df.to_string(index=False))

    os.makedirs(MODEL_DIR, exist_ok=True)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8-sig")
    print(f"\n[save] 결과 저장 -> {RESULTS_PATH}")

    best = results_df.iloc[0]
    print(f"\n[best] 최적 설정: n_estimators={int(best.n_estimators)}, "
          f"max_depth={int(best.max_depth)}, min_samples_leaf={int(best.min_samples_leaf)}")
    print("이 설정을 train_model.py에 반영하세요.")

    return results_df


if __name__ == "__main__":
    run()
