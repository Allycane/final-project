"""
feature_engineering.py (page2)
-----------------------------------
Page 2-2 "매출 예상액" 모델의 피처 엔지니어링.

Page 1과의 결정적 차이: Page 1은 모든 지역x업종 조합을 한 데이터셋으로 뭉쳐서
하나의 큰 모델을 학습했지만, Page 2-2는 사용자가 고른 "지역+업종 한 조합"의
과거 매출 추이(최대 21개 분기)만 가지고 그 조합 전용으로 회귀를 적합시킨다.
즉, 학습 데이터가 조합 하나당 15~19개 점밖에 안 되는 전형적인 시계열 예측 문제.

피처:
    - trend: 그 조합 안에서 몇 번째 분기인지 (1, 2, 3, ...) - 장기 추세
    - Q2, Q3, Q4: 계절성 더미 변수 (Q1이 기준/baseline)
    - target: monthly_sales_amount (실제 매출)

실행 위치: server/scripts/page2/feature_engineering.py
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "seoul_store.csv")

MIN_QUARTERS = 12   # 이보다 적은 분기 데이터를 가진 조합은 신뢰도가 낮아 제외
N_TEST_QUARTERS = 4  # 실제 서비스 예측 지평(4분기)과 맞춰서 백테스트도 4분기로


def load_data() -> pd.DataFrame:
    df = pd.read_csv(
        DATA_PATH, encoding="utf-8-sig", low_memory=False,
        usecols=["district_code", "service_code", "service_name",
                 "year_quarter_code", "monthly_sales_amount", "sales_data_type"],
    )
    return df


def filter_actual_only(df: pd.DataFrame) -> pd.DataFrame:
    """mock(추정치) 분기는 진짜 시장 신호가 아니므로 학습에서 아예 제외한다.
    (Page 1과 동일한 원칙 - 전체 데이터의 약 38%가 mock임을 확인함. 필터링 후
    trend는 '실측 분기들 안에서 몇 번째인지'를 나타내게 됨)"""
    before = len(df)
    df = df[df["sales_data_type"] == "actual"].copy()
    print(f"[quality_filter] {before}건 -> {len(df)}건 (mock 제외)")
    return df


def add_trend_and_season(df: pd.DataFrame) -> pd.DataFrame:
    """조합(district_code, service_code) 내에서 시간순 trend와 분기 더미 생성."""
    df = df.sort_values(["district_code", "service_code", "year_quarter_code"]).copy()

    # 조합 안에서 몇 번째 분기인지 (1부터 시작)
    df["trend"] = df.groupby(["district_code", "service_code"]).cumcount() + 1

    # year_quarter_code 마지막 자리 = 분기(1~4)
    quarter_of_year = df["year_quarter_code"] % 10
    df["is_q2"] = (quarter_of_year == 2).astype(int)
    df["is_q3"] = (quarter_of_year == 3).astype(int)
    df["is_q4"] = (quarter_of_year == 4).astype(int)

    return df


def get_eligible_groups(df: pd.DataFrame) -> pd.DataFrame:
    """MIN_QUARTERS 이상의 데이터를 가진 (지역,업종) 조합만 남김."""
    counts = df.groupby(["district_code", "service_code"])["year_quarter_code"].transform("count")
    return df[counts >= MIN_QUARTERS].copy()


def iter_series(df: pd.DataFrame):
    """(district_code, service_code)별로 그룹을 하나씩 꺼내서
    (train_df, test_df) 튜플로 반환하는 제너레이터.
    마지막 N_TEST_QUARTERS개 분기를 테스트로 뗀다 (그 조합 내에서 시간순)."""
    for (district_code, service_code), group in df.groupby(["district_code", "service_code"]):
        group = group.sort_values("year_quarter_code").reset_index(drop=True)
        if len(group) <= N_TEST_QUARTERS:
            continue
        train = group.iloc[:-N_TEST_QUARTERS]
        test = group.iloc[-N_TEST_QUARTERS:]
        yield district_code, service_code, train, test


FEATURE_COLS = ["trend", "is_q2", "is_q3", "is_q4"]
TARGET_COL = "monthly_sales_amount"


def prepare_all_series():
    """전체 파이프라인 실행 후, 백테스트에 쓸 (district_code, service_code, train, test)
    목록을 전부 반환."""
    df = load_data()
    df = filter_actual_only(df)
    df = add_trend_and_season(df)
    df = get_eligible_groups(df)
    return list(iter_series(df))