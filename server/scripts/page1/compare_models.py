"""
compare_models.py
--------------------
Page 1 "업종 추천" 모델 - 여러 알고리즘을 동일 조건(feature_engineering.py의
공용 전처리 - mock/변동성 필터링 포함)에서 비교하고, 가장 성능 좋은 모델을
최종 모델로 저장한다.

발표용 근거 자료: 왜 이 모델을 선택했는지 정량적으로 비교한 표/그래프를 만들 때 사용.
hyperparameter_tuning_deep.py보다 가볍게, "일단 어떤 알고리즘 종류가 나은지"만
빠르게 훑어보는 1차 비교 용도.

비교 대상:
    LogisticRegression, DecisionTree, RandomForest, ExtraTrees,
    GradientBoosting, HistGradientBoosting, (설치 시) XGBoost, LightGBM

실행 위치: server/scripts/page1/compare_models.py
결과물:
    - server/ml/page1/model_comparison_results.csv
    - server/ml/page1/recommendation_model.pkl (가장 성능 좋은 모델로 갱신)
"""

import os
import time
import joblib
import pandas as pd
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

# feature_engineering.py의 공용 전처리(품질 필터 포함)를 그대로 사용 -
# 여기서 데이터를 따로 다시 만들지 않는다 (다른 스크립트들과 동일 조건 비교를 위함)
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

MODEL_PATH = os.path.join(MODEL_DIR, "recommendation_model.pkl")
RESULTS_PATH = os.path.join(MODEL_DIR, "model_comparison_results.csv")


def get_candidate_models():
    models = {
        "LogisticRegression": (
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
            True,  # 스케일링 필요
        ),
        "DecisionTree": (
            DecisionTreeClassifier(max_depth=8, min_samples_leaf=10,
                                    class_weight="balanced", random_state=42),
            False,
        ),
        "RandomForest": (
            RandomForestClassifier(n_estimators=300, max_depth=10, min_samples_leaf=5,
                                    class_weight="balanced", random_state=42, n_jobs=-1),
            False,
        ),
        "ExtraTrees": (
            ExtraTreesClassifier(n_estimators=300, max_depth=10, min_samples_leaf=5,
                                  class_weight="balanced", random_state=42, n_jobs=-1),
            False,
        ),
        "GradientBoosting": (
            GradientBoostingClassifier(n_estimators=200, max_depth=3,
                                        learning_rate=0.05, random_state=42),
            False,
        ),
        "HistGradientBoosting": (
            HistGradientBoostingClassifier(max_depth=8, learning_rate=0.05, random_state=42),
            False,
        ),
    }
    if HAS_XGB:
        models["XGBoost"] = (
            XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05,
                          eval_metric="logloss", random_state=42, n_jobs=-1),
            False,
        )
    if HAS_LGBM:
        models["LightGBM"] = (
            LGBMClassifier(n_estimators=300, max_depth=8, learning_rate=0.05,
                           random_state=42, n_jobs=-1, verbose=-1),
            False,
        )
    return models


def evaluate_model(name, model, needs_scaling, X_train, y_train, X_test, y_test):
    if needs_scaling:
        scaler = StandardScaler()
        X_train_use = scaler.fit_transform(X_train)
        X_test_use = scaler.transform(X_test)
    else:
        scaler = None
        X_train_use, X_test_use = X_train, X_test

    start = time.time()
    model.fit(X_train_use, y_train)
    train_time = time.time() - start

    y_pred = model.predict(X_test_use)
    y_proba = model.predict_proba(X_test_use)[:, 1]

    result = {
        "model": name,
        "accuracy": accuracy_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "auc": roc_auc_score(y_test, y_proba),
        "train_seconds": round(train_time, 2),
    }
    return result, model, scaler


def run():
    X_train, y_train, X_test, y_test, encoders = prepare_train_test()
    print(f"[data] train={len(X_train)}건, test={len(X_test)}건\n")

    candidates = get_candidate_models()
    results = []
    fitted = {}

    for name, (model, needs_scaling) in candidates.items():
        print(f"[training] {name} ...")
        result, fitted_model, scaler = evaluate_model(
            name, model, needs_scaling, X_train, y_train, X_test, y_test
        )
        results.append(result)
        fitted[name] = (fitted_model, scaler)
        print(f"  -> accuracy={result['accuracy']:.4f}  f1={result['f1']:.4f}  "
              f"auc={result['auc']:.4f}  ({result['train_seconds']}초)")

    results_df = pd.DataFrame(results).sort_values("f1", ascending=False).reset_index(drop=True)

    print("\n=== 전체 비교 결과 (F1 기준 정렬) ===")
    print(results_df.to_string(index=False))

    os.makedirs(MODEL_DIR, exist_ok=True)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8-sig")
    print(f"\n[save] 비교표 저장 -> {RESULTS_PATH}")

    best_name = results_df.iloc[0]["model"]
    best_model, best_scaler = fitted[best_name]
    print(f"\n[best] 1차 비교 최고 모델: {best_name}")
    print("(참고: 이건 파라미터 임의값 기준 1차 비교입니다. "
          "최종 확정은 hyperparameter_tuning_deep.py 결과를 따르세요.)")

    joblib.dump(
        {
            "model": best_model,
            "model_name": best_name,
            "scaler": best_scaler,
            "encoders": encoders,
            "feature_cols": FEATURE_COLS,
            "categorical_cols": CATEGORICAL_COLS,
            "comparison_table": results_df.to_dict(orient="records"),
        },
        MODEL_PATH,
    )
    print(f"[save] 모델 저장 -> {MODEL_PATH}")

    return results_df


if __name__ == "__main__":
    run()