"""
train_gradient_boosting.py
------------------------
Page 1 "업종 추천" 모델 - GradientBoosting 버전.

[알고리즘 유형] 부스팅(Boosting) 앙상블 - 순차형
RandomForest처럼 트리를 동시에 만드는 게 아니라, 한 번에 하나씩
순서대로 만들면서 "이전 트리들이 틀린 부분"을 집중적으로 보완해나감.
정교하지만 순차 학습이라 시간이 더 오래 걸림.

전처리는 feature_engineering.py 공용 모듈을 사용 (다른 모델들과 동일 조건 비교를 위함).

실행 위치: server/scripts/page1/train_gradient_boosting.py
결과물: server/ml/page1/gradient_boosting.pkl
"""

import os
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report


from feature_engineering import prepare_train_test, FEATURE_COLS, CATEGORICAL_COLS, MODEL_DIR

MODEL_PATH = os.path.join(MODEL_DIR, "gradient_boosting.pkl")
NEEDS_SCALING = False


def train():
    X_train, y_train, X_test, y_test, encoders = prepare_train_test()

    X_train_use, X_test_use = X_train, X_test

    model = GradientBoostingClassifier(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42)
    model.fit(X_train_use, y_train)

    y_pred = model.predict(X_test_use)
    y_proba = model.predict_proba(X_test_use)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("\n=== GradientBoosting 평가 결과 ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1:       {f1:.4f}")
    print(f"AUC:      {auc:.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "model_name": "GradientBoosting",
            "scaler": None,
            "encoders": encoders,
            "feature_cols": FEATURE_COLS,
            "categorical_cols": CATEGORICAL_COLS,
            "metrics": {"accuracy": acc, "f1": f1, "auc": auc},
        },
        MODEL_PATH,
    )
    print(f"\n[save] 모델 저장 완료 -> {MODEL_PATH}")
    return {"model": "GradientBoosting", "accuracy": acc, "f1": f1, "auc": auc}


if __name__ == "__main__":
    train()
