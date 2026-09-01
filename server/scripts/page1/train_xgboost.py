"""
train_xgboost.py
------------------------
Page 1 "업종 추천" 모델 - XGBoost 버전.

[알고리즘 유형] 부스팅(Boosting) 앙상블 - 업계 표준 라이브러리
HistGradientBoosting과 같은 계열(순차적 트리 생성)이지만, 과적합 방지
정규화와 속도 최적화가 세밀하게 되어 있어 캐글 등에서 표준처럼 쓰임.
pip install xgboost 필요 (미설치 시 이 스크립트만 건너뛰어도 됨).

전처리는 feature_engineering.py 공용 모듈을 사용 (다른 모델들과 동일 조건 비교를 위함).

실행 위치: server/scripts/page1/train_xgboost.py
결과물: server/ml/page1/xgboost.pkl
"""

import os
import joblib
from xgboost import XGBClassifier  # pip install xgboost 필요
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report


from feature_engineering import prepare_train_test, FEATURE_COLS, CATEGORICAL_COLS, MODEL_DIR

MODEL_PATH = os.path.join(MODEL_DIR, "xgboost.pkl")
NEEDS_SCALING = False


def train():
    X_train, y_train, X_test, y_test, encoders = prepare_train_test()

    X_train_use, X_test_use = X_train, X_test

    model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, eval_metric="logloss", random_state=42, n_jobs=-1)
    model.fit(X_train_use, y_train)

    y_pred = model.predict(X_test_use)
    y_proba = model.predict_proba(X_test_use)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("\n=== XGBoost 평가 결과 ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1:       {f1:.4f}")
    print(f"AUC:      {auc:.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "model_name": "XGBoost",
            "scaler": None,
            "encoders": encoders,
            "feature_cols": FEATURE_COLS,
            "categorical_cols": CATEGORICAL_COLS,
            "metrics": {"accuracy": acc, "f1": f1, "auc": auc},
        },
        MODEL_PATH,
    )
    print(f"\n[save] 모델 저장 완료 -> {MODEL_PATH}")
    return {"model": "XGBoost", "accuracy": acc, "f1": f1, "auc": auc}


if __name__ == "__main__":
    train()
