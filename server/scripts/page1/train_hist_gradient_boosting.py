"""
train_hist_gradient_boosting.py
------------------------
Page 1 "업종 추천" 모델 - HistGradientBoosting 버전.

[알고리즘 유형] 부스팅(Boosting) 앙상블 - 히스토그램 최적화
GradientBoosting과 원리는 같지만, 데이터를 구간(히스토그램)으로 나눠
계산을 훨씬 빠르게 처리하는 최적화 버전. XGBoost/LightGBM과 같은 계열이며,
별도 설치 없이 scikit-learn에 내장되어 있어 바로 실행 가능.

전처리는 feature_engineering.py 공용 모듈을 사용 (다른 모델들과 동일 조건 비교를 위함).

실행 위치: server/scripts/page1/train_hist_gradient_boosting.py
결과물: server/ml/page1/hist_gradient_boosting.pkl
"""

import os
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report


from feature_engineering import prepare_train_test, FEATURE_COLS, CATEGORICAL_COLS, MODEL_DIR

MODEL_PATH = os.path.join(MODEL_DIR, "hist_gradient_boosting.pkl")
NEEDS_SCALING = False


def train():
    X_train, y_train, X_test, y_test, encoders = prepare_train_test()

    X_train_use, X_test_use = X_train, X_test

    model = HistGradientBoostingClassifier(max_depth=8, learning_rate=0.05, random_state=42)
    model.fit(X_train_use, y_train)

    y_pred = model.predict(X_test_use)
    y_proba = model.predict_proba(X_test_use)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("\n=== HistGradientBoosting 평가 결과 ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1:       {f1:.4f}")
    print(f"AUC:      {auc:.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "model_name": "HistGradientBoosting",
            "scaler": None,
            "encoders": encoders,
            "feature_cols": FEATURE_COLS,
            "categorical_cols": CATEGORICAL_COLS,
            "metrics": {"accuracy": acc, "f1": f1, "auc": auc},
        },
        MODEL_PATH,
    )
    print(f"\n[save] 모델 저장 완료 -> {MODEL_PATH}")
    return {"model": "HistGradientBoosting", "accuracy": acc, "f1": f1, "auc": auc}


if __name__ == "__main__":
    train()
