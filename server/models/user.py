from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from database.connection import Base

# 기존 UserInterest, UserRegion 별도 테이블 모델을 삭제
# users 테이블 자체에 categories/regions를 JSON 배열 컬럼으로 추가함.
class User(Base):
   __tablename__ = "users"

   id = Column(Integer, primary_key=True, index=True)
   email = Column(String(255), unique=True, nullable=False, index=True)
   password_hash = Column(String(255), nullable=False)
   name = Column(String(100), nullable=False)
   phone = Column(String(20))
   store_types = Column(JSON, default=list)
   categories = Column(JSON, default=list)
   regions = Column(JSON, default=list)
   created_at = Column(DateTime, default=datetime.utcnow)
