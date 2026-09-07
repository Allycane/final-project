"""
inference.py
--------------
Page 1 "업종 추천" 실시간 예측 모듈.

학습 스크립트(server/scripts/page1/*)와 똑같은 피처 엔지니어링 로직을 "최신 분기"에
적용해서, 실제 서비스 요청이 들어왔을 때 모델 예측 + 추천/비추천/참고 랭킹까지 계산한다.

핵심 흐름:
    1. 서버 시작 시 한 번만 recommendation_model.pkl 로드 (매 요청마다 로드하면 느림)
    2. seoul_store.csv에서 최신 분기(예: 26-1) 데이터 로드 + 피처 계산
       (전분기 대비 성장률 계산을 위해 그 이전 분기 데이터도 함께 필요)
    3. 사용자가 고른 지역(district_code) + 후보 업종(service_code 목록) 대상으로
       모델이 "다음 분기 상위 25%" 확률을 예측
    4. 그 확률 기준으로 정렬해서 상위 30%=추천, 하위 30%=비추천, 그 외 상위 하나=참고

파일 위치: server/router/inference.py
(직접 실행하는 파일이 아니라, recommend.py가 import해서 쓰는 헬퍼 모듈입니다.
 python inference.py 처럼 따로 실행하실 필요 없어요.)
"""

import os
import numpy as np
import pandas as pd
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "seoul_store.csv")
MODEL_PATH = os.path.join(BASE_DIR, "..", "ml", "page1", "recommendation_model.pkl")

FEATURE_COLS = [
    "sales_growth_rate", "net_store_change_rate", "total_store_count",
    "opening_rate", "closing_rate", "growth_pct_rank", "is_bottom25_growth",
]
CATEGORICAL_COLS = ["service_category", "district_code"]

_model_bundle = None      # 서버 시작 시 한 번만 로드해서 캐시
_latest_features_df = None  # 최신 분기 피처 계산 결과 캐시


def load_model_bundle():
    """recommendation_model.pkl 로드 (모델 + 인코더 + 스케일러 등 한 번에).
    FastAPI 앱 시작 시(main.py의 startup 이벤트) 한 번 호출해서 캐시해두는 용도."""
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(MODEL_PATH)
        print(f"[inference] 모델 로드 완료: {_model_bundle.get('model_name', 'unknown')}")
    return _model_bundle


def _compute_latest_quarter_features():
    """seoul_store.csv 전체를 읽어서, 학습 때와 동일한 방식으로 피처를 계산한 뒤
    '가장 최근 분기'(예: 26-1, 라벨은 없지만 피처는 있는 분기) 행만 추려서 반환.
    이 최근 분기 데이터가 바로 실시간 추천에 쓰이는 입력값이다."""
    global _latest_features_df
    if _latest_features_df is not None:
        return _latest_features_df

    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig", low_memory=False)
    df["service_category"] = df["service_code"].str.extract(r"(CS\d)")
    df = df[df["service_category"].isin(["CS1", "CS2", "CS3"])].copy()

    df = df.sort_values(["district_code", "service_code", "year_quarter_code"]).copy()
    grp = df.groupby(["district_code", "service_code"], group_keys=False)

    df["prev_sales"] = grp["monthly_sales_amount"].shift(1)
    df["sales_growth_rate"] = (df["monthly_sales_amount"] - df["prev_sales"]) / df["prev_sales"]
    df["net_store_change_rate"] = (
        (df["opening_store_count"] - df["closing_store_count"])
        / df["total_store_count"].replace(0, np.nan)
    )
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["sales_growth_rate", "net_store_change_rate"])

    df["growth_pct_rank"] = (
        df.groupby(["service_category", "year_quarter_code"])["sales_growth_rate"]
        .transform(lambda g: g.rank(pct=True))
    )
    df["is_bottom25_growth"] = (df["growth_pct_rank"] <= 0.25).astype(int)

    latest_quarter = df["year_quarter_code"].max()
    latest_df = df[df["year_quarter_code"] == latest_quarter].copy()

    _latest_features_df = latest_df
    print(f"[inference] 최신 분기({latest_quarter}) 피처 계산 완료: {len(latest_df)}건")
    return latest_df


def _encode_features(df: pd.DataFrame, encoders: dict) -> pd.DataFrame:
    """학습 때 만든 인코더(LabelEncoder)를 그대로 재사용해서 인코딩.
    학습 때 못 본 새 값이 있으면 -1로 처리."""
    df = df.copy()
    encoded_cols = []
    for col in CATEGORICAL_COLS:
        le = encoders[col]
        df[f"{col}_enc"] = df[col].astype(str).map(
            lambda v: le.transform([v])[0] if v in le.classes_ else -1
        )
        encoded_cols.append(f"{col}_enc")
    return df[FEATURE_COLS + encoded_cols]


def predict_growth_probability(district_code: int, service_codes: list[str]) -> pd.DataFrame:
    """지정한 지역 + 후보 업종들에 대해 '다음 분기 상위 25% 진입 확률'을 계산.
    반환: service_code, service_name, sales_growth_rate, net_store_change_rate,
          growth_probability 컬럼을 가진 DataFrame (확률 내림차순 정렬)."""
    bundle = load_model_bundle()
    model = bundle["model"]
    scaler = bundle.get("scaler")
    encoders = bundle["encoders"]

    latest_df = _compute_latest_quarter_features()

    candidates = latest_df[
        (latest_df["district_code"] == district_code)
        & (latest_df["service_code"].isin(service_codes))
    ].copy()

    if candidates.empty:
        return candidates

    X = _encode_features(candidates, encoders)
    X_use = scaler.transform(X) if scaler is not None else X

    candidates["growth_probability"] = model.predict_proba(X_use)[:, 1]

    return candidates[[
        "service_code", "service_name", "sales_growth_rate",
        "net_store_change_rate", "growth_probability",
    ]].sort_values("growth_probability", ascending=False).reset_index(drop=True)


def _describe_trend(row) -> str:
    """성장률/순증감률 수치를 자연스러운 문장으로 풀어주는 헬퍼 (배지와는 무관)."""
    growth_pct = row["sales_growth_rate"] * 100
    store_pct = row["net_store_change_rate"] * 100
    prob_pct = row["growth_probability"] * 100
    return (f"매출 {growth_pct:+.1f}%, 점포수 {store_pct:+.1f}% 추세이며, "
            f"다음 분기에도 잘될 가능성 {prob_pct:.0f}% 입니다.")


def build_recommendation_result(district_code: int, service_codes: list[str]) -> dict:
    """POST /api/recommendation 응답 형태(recommended/notRecommended/reference)로 최종 조립.

    랭킹 로직: 모델이 계산한 '다음 분기 상위 25% 진입 확률' 기준 내림차순 정렬 후
        - 확률 1등 = recommended (배지: 성장)
        - 확률 하위 30% = notRecommended (배지: 순증감률이 양수면 공급과잉, 음수면 쇠퇴)
        - 그 사이 중 최상위 1개 = reference (배지: 참고)

    배지는 quadrant(성장률/점포수 부호)가 아니라 '이 항목이 맡은 역할'에 따라 정한다.
    그래야 "추천인데 쇠퇴로 표시되는" 것 같은 모순이 안 생긴다. 실제 수치와 확률은
    description 문구에 그대로 노출해서, 왜 그렇게 판단했는지 투명하게 보여준다.
    """
    ranked = predict_growth_probability(district_code, service_codes)

    if ranked.empty:
        return {"recommended": None, "notRecommended": [], "reference": []}

    n = len(ranked)
    bottom_cut = max(1, int(np.ceil(n * 0.3)))

    top_row = ranked.iloc[0]
    bottom_pool = ranked.iloc[-bottom_cut:] if n > 1 else ranked.iloc[0:0]
    middle_pool = ranked.iloc[1: n - bottom_cut] if n > 1 + bottom_cut else ranked.iloc[0:0]

    recommended = {
        "name": top_row["service_name"],
        "badge": "성장",
        "description": _describe_trend(top_row),
    }

    not_recommended = []
    for _, row in bottom_pool.iterrows():
        badge = "공급과잉" if row["net_store_change_rate"] >= 0 else "쇠퇴"
        not_recommended.append({
            "name": row["service_name"],
            "badge": badge,
            "description": _describe_trend(row),
        })

    reference = []
    if len(middle_pool) > 0:
        mid_row = middle_pool.iloc[0]
        reference.append({
            "name": mid_row["service_name"],
            "badge": "참고",
            "description": _describe_trend(mid_row),
        })

    return {
        "recommended": recommended,
        "notRecommended": not_recommended,
        "reference": reference,
    }
