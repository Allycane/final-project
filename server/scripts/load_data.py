"""
load_data.py
------------
location.csv, seoul_store.csv를 MySQL(fp_db)의 location, store 테이블에 적재.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ── DB 연결 설정 ──────────────────────────────
# .env 파일(server/.env)에서 DB 접속 정보를 읽어온다.
# .env 예시:
#   DB_USER=admin
#   DB_PASSWORD=mysql1234
#   DB_HOST=mysql1.c3280mk20lzj.ap-northeast-2.rds.amazonaws.com
#   DB_PORT=3306
#   DB_NAME=fp_db

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

missing = [k for k, v in {
    "DB_USER": DB_USER, "DB_PASSWORD": DB_PASSWORD,
    "DB_HOST": DB_HOST, "DB_NAME": DB_NAME,
}.items() if not v]
if missing:
    raise RuntimeError(
        f".env에서 다음 값을 찾을 수 없습니다: {missing}. "
        f"이 스크립트와 같은 폴더(또는 상위 폴더)에 .env 파일이 있는지 확인하세요."
    )

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# 이 스크립트는 final-project/server/scripts/ 에 위치한다고 가정.
# data 폴더는 한 단계 위(server/data)에 있으므로 상대경로로 접근.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data")


def load_location():
    path = os.path.join(DATA_PATH, "location.csv")
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)

    print("[location] columns:", df.columns.tolist())
    print("[location] shape:", df.shape)
    print("[location] NA counts:\n", df.isna().sum())

    # location 테이블 실제 컬럼만 남기기 (geo_point는 GENERATED 컬럼이라 제외)
    loc_cols = [
        "district_code", "district_name", "longitude", "latitude",
        "service_code", "service_name",
    ]
    df = df[loc_cols].copy()

    # longitude/latitude가 문자열로 읽힌 경우를 대비해 숫자로 강제 변환.
    # 변환 안 되는 값은 NaN이 되므로, 그런 행이 있으면 먼저 원인을 보여주고 중단한다.
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")

    bad_mask = df["longitude"].isna() | df["latitude"].isna()
    if bad_mask.any():
        bad_path = os.path.join(DATA_PATH, "location_bad_rows.csv")
        df.loc[bad_mask].to_csv(bad_path, index=False, encoding="utf-8-sig")
        print(
            f"[location] 좌표 결측 {bad_mask.sum()}건 발견 (전체의 "
            f"{bad_mask.sum() / len(df):.3%}) → '{bad_path}'에 저장하고 적재 대상에서 제외합니다."
        )
        df = df.loc[~bad_mask].copy()

    # 좌표 범위 검증 (SRID 4326 위경도 범위를 벗어나면 INSERT 시 에러 발생)
    lon_out = ~df["longitude"].between(-180, 180)
    lat_out = ~df["latitude"].between(-90, 90)
    if lon_out.any() or lat_out.any():
        out_path = os.path.join(DATA_PATH, "location_out_of_range.csv")
        df.loc[lon_out | lat_out].to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"[location] 범위 이상치 longitude={lon_out.sum()}건, latitude={lat_out.sum()}건")
        print(df.loc[lon_out | lat_out].head(20))
        print(f"[location] 전체 목록 '{out_path}'에 저장, 적재 대상에서 제외합니다.")
        df = df.loc[~(lon_out | lat_out)].copy()

    assert df["longitude"].between(-180, 180).all(), "경도 범위 이상치 존재"
    assert df["latitude"].between(-90, 90).all(), "위도 범위 이상치 존재"

    df.to_sql(
        "location",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )
    print(f"[location] 적재 완료: {len(df)}건\n")


def load_store():
    path = os.path.join(DATA_PATH, "seoul_store.csv")
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)

    print("[store] columns:", df.columns.tolist())
    print("[store] shape:", df.shape)
    print("[store] sales_data_type 분포:\n", df["sales_data_type"].value_counts())

    # store 테이블 실제 컬럼만 남기기 (service_category는 GENERATED 컬럼이라 제외)
    store_cols = [
        "year_quarter_code", "district_code", "district_name",
        "service_code", "service_name", "total_store_count",
        "opening_rate", "opening_store_count", "closing_rate",
        "closing_store_count", "monthly_sales_amount",
        "male_sales_amount", "female_sales_amount", "sales_data_type",
    ]
    df = df[store_cols]

    df.to_sql(
        "store",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )
    print(f"[store] 적재 완료: {len(df)}건\n")


def verify():
    with engine.connect() as conn:
        loc_count = conn.execute(text("SELECT COUNT(*) FROM location")).scalar()
        store_count = conn.execute(text("SELECT COUNT(*) FROM store")).scalar()
        type_dist = conn.execute(
            text("SELECT sales_data_type, COUNT(*) FROM store GROUP BY sales_data_type")
        ).fetchall()

        print("=== 적재 결과 검증 ===")
        print("location 총 건수:", loc_count)
        print("store 총 건수:", store_count)
        print("store sales_data_type 분포:", type_dist)


if __name__ == "__main__":
    load_location()
    load_store()
    verify()