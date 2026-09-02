"""
hyperparameter_tuning_deep.py
--------------------------------
hyperparameter_tuning.py보다 훨씬 넓은 범위로 하이퍼파라미터를 탐색하는 심화 버전.

기존 GridSearchCV(격자 전체 탐색) 대신 RandomizedSearchCV(넓은 범위에서 무작위 표본 추출)를
사용한다. 이유:
    - 파라미터를 3개→5~7개로 늘리면 격자 조합 수가 수천~수만 개로 폭발적으로 늘어남
    - RandomizedSearchCV는 몇 개를 시도할지(N_ITER)를 직접 정할 수 있어서,
      파라미터를 아무리 늘려도 총 소요 시간을 예측 가능한 범위로 유지할 수 있음
    - 연속적인 범위(예: learning_rate 0.001~0.3 사이 아무 값)에서 뽑기 때문에,
      격자보다 더 미세한 값도 탐색 가능

교차검증도 4-Fold -> 5-Fold로 늘려서 더 안정적인 평균을 얻는다.

실행 위치: server/scripts/page1/hyperparameter_tuning_deep.py
결과물: server/ml/page1/hyperparameter_tuning_deep_results.csv
        server/ml/page1/recommendation_model.pkl (덮어씀 - 심화 탐색 결과가 최신)

예상 소요 시간: 모델당 N_ITER(기본 500)회 x 8-Fold = 4,000회 학습.
    8개 모델이면 총 32,000회 안팎. 시간이 매우 오래 걸릴 수 있음(수 시간~하루 이상 가능).
    급하면 파일 아래쪽 N_ITER 값을 줄이면 비례해서 빨라짐.
"""

import os
import time
import warnings
import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")  # 장시간 실행 중 sklearn 경고 메시지로 콘솔 도배되는 것 방지
from scipy.stats import randint, uniform, loguniform
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
)
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from feature_engineering import prepare_train_test, FEATURE_COLS, CATEGORICAL_COLS, MODEL_DIR

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("[info] xgboost 미설치 - 비교 대상에서 제외합니다.")

try:
    from lightgbm import LGBMClassifier
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False
    print("[info] lightgbm 미설치 - 비교 대상에서 제외합니다.")

RESULTS_PATH = os.path.join(MODEL_DIR, "hyperparameter_tuning_deep_results.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "recommendation_model.pkl")

N_CV_SPLITS = 8      # 8-Fold로 더 촘촘하고 안정적인 평균
N_ITER = 500          # 모델당 무작위로 시도할 조합 수 (늘릴수록 정교해지지만 느려짐)
RANDOM_STATE = 42


# ── 모델별 "탐색 범위" (고정값 목록이 아니라 분포/범위로 지정) ──────────
# randint(a, b): a 이상 b 미만 정수 중 무작위
# uniform(a, w): a 이상 a+w 미만 실수 중 무작위 (균등분포)
# loguniform(a, b): a~b 사이를 로그스케일로 균등하게 뽑음 (learning_rate처럼
#                    작은 값 구간이 중요한 파라미터에 적합)

PARAM_DISTS = {
    "LogisticRegression": {
        "estimator": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
        "needs_scaling": True,
        "param_dist": {
            "C": loguniform(1e-4, 1e3),
            "penalty": ["l1", "l2"],
            "solver": ["liblinear"],  # l1, l2 둘 다 지원하는 solver
        },
    },
    "DecisionTree": {
        "estimator": DecisionTreeClassifier(class_weight="balanced", random_state=RANDOM_STATE),
        "needs_scaling": False,
        "param_dist": {
            "max_depth": randint(2, 20),
            "min_samples_leaf": randint(2, 100),
            "min_samples_split": randint(2, 50),
            "max_features": [None, "sqrt", "log2"],
        },
    },
    "RandomForest": {
        "estimator": RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
        "needs_scaling": False,
        "param_dist": {
            "n_estimators": randint(100, 600),
            "max_depth": randint(4, 20),
            "min_samples_leaf": randint(2, 50),
            "min_samples_split": randint(2, 30),
            "max_features": ["sqrt", "log2", None],
            "bootstrap": [True, False],
        },
    },
    "ExtraTrees": {
        "estimator": ExtraTreesClassifier(class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
        "needs_scaling": False,
        "param_dist": {
            "n_estimators": randint(100, 600),
            "max_depth": randint(4, 20),
            "min_samples_leaf": randint(2, 50),
            "min_samples_split": randint(2, 30),
            "max_features": ["sqrt", "log2", None],
        },
    },
    "GradientBoosting": {
        "estimator": GradientBoostingClassifier(random_state=RANDOM_STATE),
        "needs_scaling": False,
        "param_dist": {
            "n_estimators": randint(50, 400),
            "max_depth": randint(2, 8),
            "learning_rate": loguniform(0.005, 0.3),
            "subsample": uniform(0.5, 0.5),       # 0.5 ~ 1.0
            "max_features": ["sqrt", "log2", None],
            "min_samples_leaf": randint(2, 50),
        },
    },
    "HistGradientBoosting": {
        "estimator": HistGradientBoostingClassifier(random_state=RANDOM_STATE),
        "needs_scaling": False,
        "param_dist": {
            "max_depth": randint(3, 16),
            "learning_rate": loguniform(0.005, 0.3),
            "max_iter": randint(50, 500),
            "max_leaf_nodes": randint(15, 255),
            "l2_regularization": uniform(0.0, 1.0),
            "min_samples_leaf": randint(5, 100),
        },
    },
}

if HAS_XGB:
    PARAM_DISTS["XGBoost"] = {
        "estimator": XGBClassifier(eval_metric="logloss", random_state=RANDOM_STATE, n_jobs=-1),
        "needs_scaling": False,
        "param_dist": {
            "n_estimators": randint(50, 600),
            "max_depth": randint(2, 10),
            "learning_rate": loguniform(0.005, 0.3),
            "subsample": uniform(0.5, 0.5),
            "colsample_bytree": uniform(0.5, 0.5),
            "min_child_weight": randint(1, 10),
            "reg_alpha": loguniform(1e-3, 10),
            "reg_lambda": loguniform(1e-3, 10),
        },
    }

if HAS_LGBM:
    PARAM_DISTS["LightGBM"] = {
        "estimator": LGBMClassifier(random_state=RANDOM_STATE, n_jobs=-1, verbose=-1),
        "needs_scaling": False,
        "param_dist": {
            "n_estimators": randint(50, 600),
            "max_depth": randint(2, 12),
            "num_leaves": randint(15, 255),
            "learning_rate": loguniform(0.005, 0.3),
            "subsample": uniform(0.5, 0.5),
            "colsample_bytree": uniform(0.5, 0.5),
            "reg_alpha": loguniform(1e-3, 10),
            "reg_lambda": loguniform(1e-3, 10),
        },
    }


def tune_one_model(name, config, X_train, y_train, X_test, y_test):
    print(f"\n[tuning] {name} - {N_ITER}개 무작위 조합 탐색 중 ...")

    needs_scaling = config["needs_scaling"]
    scaler = None
    if needs_scaling:
        scaler = StandardScaler()
        X_train_use = scaler.fit_transform(X_train)
        X_test_use = scaler.transform(X_test)
    else:
        X_train_use, X_test_use = X_train, X_test

    tscv = TimeSeriesSplit(n_splits=N_CV_SPLITS)

    search = RandomizedSearchCV(
        estimator=config["estimator"],
        param_distributions=config["param_dist"],
        n_iter=N_ITER,
        scoring="f1",
        cv=tscv,
        n_jobs=-1,
        random_state=RANDOM_STATE,
        refit=True,
    )

    start = time.time()
    search.fit(X_train_use, y_train)
    tuning_time = time.time() - start

    best_model = search.best_estimator_
    y_pred = best_model.predict(X_test_use)
    y_proba = best_model.predict_proba(X_test_use)[:, 1]

    result = {
        "model": name,
        "best_params": str(search.best_params_),
        "cv_f1_mean": round(search.best_score_, 4),
        "test_accuracy": round(accuracy_score(y_test, y_pred), 4),
        "test_f1": round(f1_score(y_test, y_pred), 4),
        "test_auc": round(roc_auc_score(y_test, y_proba), 4),
        "n_iter": N_ITER,
        "tuning_seconds": round(tuning_time, 1),
    }

    print(f"  최적 파라미터: {search.best_params_}")
    print(f"  교차검증 F1 평균: {search.best_score_:.4f}  |  테스트 F1: {result['test_f1']:.4f}  "
          f"|  테스트 AUC: {result['test_auc']:.4f}  ({tuning_time:.1f}초)")

    return result, best_model, scaler


def run():
    X_train, y_train, X_test, y_test, encoders = prepare_train_test()
    print(f"[data] train={len(X_train)}건, test={len(X_test)}건")
    print(f"[cv] TimeSeriesSplit(n_splits={N_CV_SPLITS}), 모델당 {N_ITER}개 무작위 조합 시도")
    print(f"[전체] {len(PARAM_DISTS)}개 모델 x {N_ITER}개 조합 x {N_CV_SPLITS}-Fold = "
          f"약 {len(PARAM_DISTS) * N_ITER * N_CV_SPLITS}회 모델 학습 예정\n")

    results = []
    fitted_models = {}

    for name, config in PARAM_DISTS.items():
        result, best_model, scaler = tune_one_model(name, config, X_train, y_train, X_test, y_test)
        results.append(result)
        fitted_models[name] = (best_model, scaler)

        # 모델 하나 끝날 때마다 즉시 중간 저장
        os.makedirs(MODEL_DIR, exist_ok=True)
        partial_df = pd.DataFrame(results).sort_values("test_f1", ascending=False).reset_index(drop=True)
        partial_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8-sig")
        print(f"  [중간저장] 지금까지 {len(results)}개 모델 결과 -> {RESULTS_PATH}\n")

    results_df = pd.DataFrame(results).sort_values("test_f1", ascending=False).reset_index(drop=True)

    print("\n=== 심화 탐색 최종 결과 (테스트 F1 기준 정렬) ===")
    print(results_df.to_string(index=False))

    best_name = results_df.iloc[0]["model"]
    best_model, best_scaler = fitted_models[best_name]
    print(f"\n[best] 최종 채택 모델: {best_name}")

    joblib.dump(
        {
            "model": best_model,
            "model_name": best_name,
            "scaler": best_scaler,
            "encoders": encoders,
            "feature_cols": FEATURE_COLS,
            "categorical_cols": CATEGORICAL_COLS,
            "tuning_results": results_df.to_dict(orient="records"),
        },
        MODEL_PATH,
    )
    print(f"[save] 최종 모델 저장 -> {MODEL_PATH}")

    return results_df


if __name__ == "__main__":
    run()