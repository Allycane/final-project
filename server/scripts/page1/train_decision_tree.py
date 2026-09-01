"""
train_decision_tree.py
------------------------
DecisionTree 버전.

[알고리즘 유형] 단일 결정트리
"성장률 5% 이상인가? -> 순증감률 0 이상인가?" 처럼 질문을 반복하며
데이터를 나누는 모델. 이해하기 쉽지만 트리 하나만 쓰면 학습 데이터에
과적합되기 쉬움 -> 이후 모델들은 트리를 여러 개 조합해 이를 보완함.

전처리는 feature_engineering.py 공용 모듈을 사용 (다른 모델들과 동일 조건 비교를 위함).

실행 위치: server/scripts/page1/train_decision_tree.py
결과물: server/ml/page1/decision_tree.pkl
"""

import os
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report


from feature_engineering import prepare_train_test, FEATURE_COLS, CATEGORICAL_COLS, MODEL_DIR

MODEL_PATH = os.path.join(MODEL_DIR, "decision_tree.pkl")
NEEDS_SCALING = False


def train():
    X_train, y_train, X_test, y_test, encoders = prepare_train_test()

    X_train_use, X_test_use = X_train, X_test

    model = DecisionTreeClassifier(max_depth=8, min_samples_leaf=10, class_weight="balanced", random_state=42)
    model.fit(X_train_use, y_train)

    y_pred = model.predict(X_test_use)
    y_proba = model.predict_proba(X_test_use)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("\n=== DecisionTree 평가 결과 ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1:       {f1:.4f}")
    print(f"AUC:      {auc:.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "model_name": "DecisionTree",
            "scaler": None,
            "encoders": encoders,
            "feature_cols": FEATURE_COLS,
            "categorical_cols": CATEGORICAL_COLS,
            "metrics": {"accuracy": acc, "f1": f1, "auc": auc},
        },
        MODEL_PATH,
    )
    print(f"\n[save] 모델 저장 완료 -> {MODEL_PATH}")
    return {"model": "DecisionTree", "accuracy": acc, "f1": f1, "auc": auc}


if __name__ == "__main__":
    train()
