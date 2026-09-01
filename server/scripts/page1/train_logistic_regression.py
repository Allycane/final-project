"""
train_logistic_regression.py
------------------------
Page 1 "업종 추천" 모델 - LogisticRegression 버전.

[알고리즘 유형] 선형 모델 (베이스라인)
각 피처(성장률, 순증감률 등)에 가중치를 곱해 더한 뒤 0~1 확률로 변환하는
가장 단순한 모델. 직선적인 관계만 학습 가능해서, 다른 복잡한 모델들이
이보다 얼마나 더 나은지 비교하는 "기준점" 역할.

전처리는 feature_engineering.py 공용 모듈을 사용 (다른 모델들과 동일 조건 비교를 위함).

실행 위치: server/scripts/page1/train_logistic_regression.py
결과물: server/ml/page1/logistic_regression.pkl
"""

import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler

from feature_engineering import prepare_train_test, FEATURE_COLS, CATEGORICAL_COLS, MODEL_DIR

MODEL_PATH = os.path.join(MODEL_DIR, "logistic_regression.pkl")
NEEDS_SCALING = True


def train():
    X_train, y_train, X_test, y_test, encoders = prepare_train_test()

    scaler = StandardScaler()
    X_train_use = scaler.fit_transform(X_train)
    X_test_use = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    model.fit(X_train_use, y_train)

    y_pred = model.predict(X_test_use)
    y_proba = model.predict_proba(X_test_use)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("\n=== LogisticRegression 평가 결과 ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1:       {f1:.4f}")
    print(f"AUC:      {auc:.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "model_name": "LogisticRegression",
            "scaler": scaler,
            "encoders": encoders,
            "feature_cols": FEATURE_COLS,
            "categorical_cols": CATEGORICAL_COLS,
            "metrics": {"accuracy": acc, "f1": f1, "auc": auc},
        },
        MODEL_PATH,
    )
    print(f"\n[save] 모델 저장 완료 -> {MODEL_PATH}")
    return {"model": "LogisticRegression", "accuracy": acc, "f1": f1, "auc": auc}


if __name__ == "__main__":
    train()
