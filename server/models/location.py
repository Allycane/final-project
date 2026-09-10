# CSV로 업로드된 매장 좌표 데이터 테이블(location) 모델.
# scripts/load_data.py가 server/data/location.csv를 이 테이블에 적재한다
# (store 테이블과 동일하게 id는 DB에서 자동 증가로 넣음

# 컬럼 
# district_code / district_name: 자치구 코드/명 (예: "11680" / "강남구")
# longitude / latitude: 경도 / 위도
# service_code / service_name: 업종 코드/명 (예: "CS100001" / "한식음식점")

# longitude/latitude로 직접 계산한다.

from sqlalchemy import Column, Integer, String, Float

from database.connection import Base


class Location(Base):
    __tablename__ = "location"

    id = Column(Integer, primary_key=True, index=True)
    district_code = Column(String(20), index=True)
    district_name = Column(String(100), index=True)
    longitude = Column(Float)
    latitude = Column(Float)
    service_code = Column(String(20), index=True)
    service_name = Column(String(100), index=True)
