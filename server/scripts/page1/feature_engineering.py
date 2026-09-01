"""
feature_engineering.py
------------------------
Page 1 "업종 추천" 모델들이 공통으로 쓰는 데이터 전처리/피처 생성 로직.
모든 개별 모델 학습 스크립트(train_*.py)가 이 모듈을 import해서 사용한다.
→ 모델마다 전처리 로직이 달라지면 공정한 비교가 안 되므로, 반드시 여기서만 수정할 것.

실행 위치 기준: server/scripts/feature_engineering.py
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# server/scripts/page1/ 에 위치하므로 server/까지 두 단계 위로 올라가야 함
DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "seoul_store.csv")
MODEL_DIR = os.path.join(BASE_DIR, "..", "..", "ml", "page1")

N_TEST_QUARTERS = 4
TOP_PCT = 0.25
BOTTOM_PCT = 0.25

FEATURE_COLS = [
    "sales_growth_rate", "net_store_change_rate", "total_store_count",
    "opening_rate", "closing_rate", "growth_pct_rank", "is_bottom25_growth",
]
CATEGORICAL_COLS = ["service_category", "district_code"]


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig", low_memory=False)
    print(f"[load] shape={df.shape}")
    return df


def add_service_category(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["service_category"] = df["service_code"].str.extract(r"(CS\d)")
    return df[df["service_category"].isin(["CS1", "CS2", "CS3"])].copy()


def add_growth_and_net_change(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["district_code", "service_code", "year_quarter_code"]).copy()
    grp = df.groupby(["district_code", "service_code"], group_keys=False)

    df["prev_sales"] = grp["monthly_sales_amount"].shift(1)
    df["sales_growth_rate"] = (df["monthly_sales_amount"] - df["prev_sales"]) / df["prev_sales"]
    df["net_store_change_rate"] = (
        (df["opening_store_count"] - df["closing_store_count"])
        / df["total_store_count"].replace(0, np.nan)
    )

    df = df.replace([np.inf, -np.inf], np.nan)
    return df.dropna(subset=["sales_growth_rate", "net_store_change_rate"])


def add_percentile_labels(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["growth_pct_rank"] = (
        df.groupby(["service_category", "year_quarter_code"])["sales_growth_rate"]
        .transform(lambda g: g.rank(pct=True))
    )
    df["is_top25_growth"] = (df["growth_pct_rank"] >= (1 - TOP_PCT)).astype(int)
    df["is_bottom25_growth"] = (df["growth_pct_rank"] <= BOTTOM_PCT).astype(int)
    return df


def add_next_quarter_label(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["district_code", "service_code", "year_quarter_code"]).copy()
    grp = df.groupby(["district_code", "service_code"], group_keys=False)
    df["target_next_top25"] = grp["is_top25_growth"].shift(-1)
    df = df.dropna(subset=["target_next_top25"])
    df["target_next_top25"] = df["target_next_top25"].astype(int)
    return df


def build_features(df: pd.DataFrame, encoders=None):
    df = df.copy()
    fresh = encoders is None
    if fresh:
        encoders = {}

    encoded_cols = []
    for col in CATEGORICAL_COLS:
        if fresh:
            le = LabelEncoder()
            df[f"{col}_enc"] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            le = encoders[col]
            df[f"{col}_enc"] = df[col].astype(str).map(
                lambda v: le.transform([v])[0] if v in le.classes_ else -1
            )
        encoded_cols.append(f"{col}_enc")

    X = df[FEATURE_COLS + encoded_cols].copy()
    y = df["target_next_top25"] if "target_next_top25" in df.columns else None
    return X, y, encoders


def time_split(df: pd.DataFrame):
    quarters = sorted(df["year_quarter_code"].unique())
    test_quarters = quarters[-N_TEST_QUARTERS:]
    train_quarters = quarters[:-N_TEST_QUARTERS]
    train_df = df[df["year_quarter_code"].isin(train_quarters)].copy()
    test_df = df[df["year_quarter_code"].isin(test_quarters)].copy()
    return train_df, test_df


def prepare_train_test():
    """전처리 전체 파이프라인 실행 후 (X_train, y_train, X_test, y_test, encoders) 반환.
    모든 train_*.py 스크립트의 첫 줄에서 이 함수 하나만 호출하면 됨."""
    df = load_data()
    df = add_service_category(df)
    df = add_growth_and_net_change(df)
    df = add_percentile_labels(df)
    df = add_next_quarter_label(df)

    train_df, test_df = time_split(df)
    X_train, y_train, encoders = build_features(train_df)
    X_test, y_test, _ = build_features(test_df, encoders=encoders)

    print(f"[data] train={len(X_train)}건, test={len(X_test)}건")
    return X_train, y_train, X_test, y_test, encoders