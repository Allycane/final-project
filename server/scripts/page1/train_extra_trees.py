"""
train_extra_trees.py
------------------------
Page 1 "업종 추천" 모델 - ExtraTrees 버전.

[알고리즘 유형] 배깅(Bagging) 앙상블 - RandomForest 변형
RandomForest와 원리는 같지만, 트리를 나눌 기준을 계산해서 고르는 대신
더 랜덤하게 정함. 계산량이 줄어 학습이 더 빠르고, 트리 간 다양성이
커져 과적합을 더 줄일 수 있음.

전처리는 feature_engineering.py 공용 모듈을 사용 (다른 모델들과 동일 조건 비교를 위함).

실행 위치: server/scripts/page1/train_extra_trees.py
결과물: server/ml/page1/extra_trees.pkl
"""

import os
import joblib
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report


from feature_engineering import prepare_train_test, FEATURE_COLS, CATEGORICAL_COLS, MODEL_DIR

MODEL_PATH = os.path.join(MODEL_DIR, "extra_trees.pkl")
NEEDS_SCALING = False


def train():
    X_train, y_train, X_test, y_test, encoders = prepare_train_test()

    X_train_use, X_test_use = X_train, X_test

    model = ExtraTreesClassifier(n_estimators=300, max_depth=10, min_samples_leaf=5, class_weight="balanced", random_state=42, n_jobs=-1)
    model.fit(X_train_use, y_train)

    y_pred = model.predict(X_test_use)
    y_proba = model.predict_proba(X_test_use)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("\n=== ExtraTrees 평가 결과 ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1:       {f1:.4f}")
    print(f"AUC:      {auc:.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "model_name": "ExtraTrees",
            "scaler": None,
            "encoders": encoders,
            "feature_cols": FEATURE_COLS,
            "categorical_cols": CATEGORICAL_COLS,
            "metrics": {"accuracy": acc, "f1": f1, "auc": auc},
        },
        MODEL_PATH,
    )
    print(f"\n[save] 모델 저장 완료 -> {MODEL_PATH}")
    return {"model": "ExtraTrees", "accuracy": acc, "f1": f1, "auc": auc}


if __name__ == "__main__":
    train()
