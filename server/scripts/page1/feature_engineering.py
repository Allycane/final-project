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
    df["prev_sales_data_type"] = grp["sales_data_type"].shift(1)
    df["sales_growth_rate"] = (df["monthly_sales_amount"] - df["prev_sales"]) / df["prev_sales"]
    df["net_store_change_rate"] = (
        (df["opening_store_count"] - df["closing_store_count"])
        / df["total_store_count"].replace(0, np.nan)
    )

    df = df.replace([np.inf, -np.inf], np.nan)
    return df.dropna(subset=["sales_growth_rate", "net_store_change_rate"])


# 실시간 서비스(router/inference.py)와 반드시 동일하게 맞춰야 하는 데이터 품질 기준.
# 이 값이 서로 달라지면 "서비스에서는 안 보여주는 조건인데 모델은 그걸로 학습한"
# 불일치가 생기므로, 두 파일 다 고칠 때 함께 맞춰야 한다.
VOLATILITY_THRESHOLD = 0.5


def add_quality_filter(df: pd.DataFrame) -> pd.DataFrame:
    """실시간 서비스와 동일한 기준으로 학습 데이터도 정제한다.
    1) 이번 분기 또는 전분기 매출이 mock(추정치)이면 성장률이 진짜 시장 신호가
       아니므로 제외 (전체 데이터의 약 38%가 mock으로 확인됨)
    2) 실측이어도 성장률 절대값이 50% 이상이면(부동산중개업처럼 원래 변동성이
       큰 업종) 과적합 위험이 있는 극단치이므로 제외
    이렇게 해야 "서비스에서는 안 보여줄 데이터로 모델이 학습되는" 불일치를 막는다."""
    before = len(df)
    is_mock = (df["sales_data_type"] != "actual") | (df["prev_sales_data_type"] != "actual")
    is_volatile = (~is_mock) & (df["sales_growth_rate"].abs() >= VOLATILITY_THRESHOLD)

    df = df[~(is_mock | is_volatile)].copy()
    print(f"[quality_filter] {before}건 -> {len(df)}건 "
          f"(mock {is_mock.sum()}건, 변동성과다 {is_volatile.sum()}건 제외)")
    return df


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
    """다음 분기 라벨을 만든다. 품질 필터링 때문에 한 조합의 분기 시퀀스에
    '구멍'(중간 분기가 빠짐)이 생길 수 있어서, 단순히 그룹 내 다음 행을 쓰는
    shift(-1) 방식은 위험하다 (구멍 바로 다음 분기를 진짜 다음 분기로 착각할 수 있음).
    대신 실제 분기 코드 순서를 기준으로 '진짜 바로 다음 분기'가 몇 번인지 계산해서,
    그 분기의 데이터가 실제로 존재할 때만 라벨을 붙인다."""
    df = df.sort_values(["district_code", "service_code", "year_quarter_code"]).copy()

    quarters_sorted = sorted(df["year_quarter_code"].unique())
    quarter_to_next = {q: quarters_sorted[i + 1] for i, q in enumerate(quarters_sorted[:-1])}
    df["expected_next_quarter"] = df["year_quarter_code"].map(quarter_to_next)

    label_source = df[["district_code", "service_code", "year_quarter_code", "is_top25_growth"]].rename(
        columns={"year_quarter_code": "expected_next_quarter", "is_top25_growth": "target_next_top25"}
    )

    df = df.merge(label_source, on=["district_code", "service_code", "expected_next_quarter"], how="left")
    df = df.dropna(subset=["target_next_top25", "expected_next_quarter"])
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
    df = add_quality_filter(df)
    df = add_percentile_labels(df)
    df = add_next_quarter_label(df)

    train_df, test_df = time_split(df)
    X_train, y_train, encoders = build_features(train_df)
    X_test, y_test, _ = build_features(test_df, encoders=encoders)

    print(f"[data] train={len(X_train)}건, test={len(X_test)}건")
    return X_train, y_train, X_test, y_test, encoders