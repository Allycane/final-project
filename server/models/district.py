"""
CSV로 업로드된 상권 데이터 테이블(store) 모델.

컬럼 설명:
- year_quarter_code: 20261 처럼 "연도+분기" 형태 (연도=code//10, 분기=code%10)
- district_code / district_name: 자치구 코드/명 (예: "강동구")
- service_code / service_name: 업종 코드/명 (예: "CS300043", "전자상거래업")
- service_category: 업종 대분류 코드 (예: "CS3") - 회원 categories와는 매칭에 사용하지 않음
- total_store_count: 해당 분기 총 점포 수
- opening_rate / opening_store_count: 개업률 / 개업 점포 수
- closing_rate / closing_store_count: 폐업률 / 폐업 점포 수
- monthly_sales_amount: 월 매출액 (원)
- male_sales_amount / female_sales_amount: 성별 매출액 (원)
- sales_data_type: "actual"(실측) 또는 "mock"(추정/샘플) 데이터 구분
"""
from sqlalchemy import Column, BigInteger, Integer, String, Float

from database.connection import Base


class CommercialDistrict(Base):
    __tablename__ = "store"

    id = Column(Integer, primary_key=True, index=True)
    year_quarter_code = Column(Integer, index=True)
    district_code = Column(String(20), index=True)
    district_name = Column(String(100), index=True)
    service_code = Column(String(20), index=True)
    service_name = Column(String(100), index=True)
    service_category = Column(String(20), index=True)
    total_store_count = Column(Integer, nullable=True)
    opening_rate = Column(Float, nullable=True)
    opening_store_count = Column(Integer, nullable=True)
    closing_rate = Column(Float, nullable=True)
    closing_store_count = Column(Integer, nullable=True)
    monthly_sales_amount = Column(BigInteger, nullable=True)
    male_sales_amount = Column(BigInteger, nullable=True)
    female_sales_amount = Column(BigInteger, nullable=True)
    sales_data_type = Column(String(20), nullable=True)
