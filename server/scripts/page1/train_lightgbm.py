"""
train_lightgbm.py
------------------------
Page 1 "업종 추천" 모델 - LightGBM 버전.

[알고리즘 유형] 부스팅(Boosting) 앙상블 - 대용량 데이터 특화
XGBoost와 목적은 같지만 트리 성장 방식이 다름. 보통 트리는 층층이(레벨 단위)
자라는데, LightGBM은 가장 효과 좋은 방향으로 세로로 깊게 먼저 자람
(leaf-wise). 대용량 데이터에서 특히 빠르고 메모리 사용량도 적음.
pip install lightgbm 필요 (미설치 시 이 스크립트만 건너뛰어도 됨).

전처리는 feature_engineering.py 공용 모듈을 사용 (다른 모델들과 동일 조건 비교를 위함).

실행 위치: server/scripts/page1/train_lightgbm.py
결과물: server/ml/page1/lightgbm.pkl
"""

import os
import joblib
from lightgbm import LGBMClassifier  # pip install lightgbm 필요
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report


from feature_engineering import prepare_train_test, FEATURE_COLS, CATEGORICAL_COLS, MODEL_DIR

MODEL_PATH = os.path.join(MODEL_DIR, "lightgbm.pkl")
NEEDS_SCALING = False


def train():
    X_train, y_train, X_test, y_test, encoders = prepare_train_test()

    X_train_use, X_test_use = X_train, X_test

    model = LGBMClassifier(n_estimators=300, max_depth=8, learning_rate=0.05, random_state=42, n_jobs=-1, verbose=-1)
    model.fit(X_train_use, y_train)

    y_pred = model.predict(X_test_use)
    y_proba = model.predict_proba(X_test_use)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("\n=== LightGBM 평가 결과 ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1:       {f1:.4f}")
    print(f"AUC:      {auc:.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "model_name": "LightGBM",
            "scaler": None,
            "encoders": encoders,
            "feature_cols": FEATURE_COLS,
            "categorical_cols": CATEGORICAL_COLS,
            "metrics": {"accuracy": acc, "f1": f1, "auc": auc},
        },
        MODEL_PATH,
    )
    print(f"\n[save] 모델 저장 완료 -> {MODEL_PATH}")
    return {"model": "LightGBM", "accuracy": acc, "f1": f1, "auc": auc}


if __name__ == "__main__":
    train()
