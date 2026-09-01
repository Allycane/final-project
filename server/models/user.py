from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from database.connection import Base

# ===== 수정 시작 (관심사 저장 구조 변경, 2026-09-01) =====
# 기존 UserInterest, UserRegion 별도 테이블 모델을 삭제하고,
# users 테이블 자체에 categories/regions를 JSON 배열 컬럼으로 추가함.
# 회원 한 명당 한 행에 관심사 리스트를 통째로 저장.
class User(Base):
   __tablename__ = "users"

   id = Column(Integer, primary_key=True, index=True)
   email = Column(String(255), unique=True, nullable=False, index=True)
   password_hash = Column(String(255), nullable=False)
   name = Column(String(100), nullable=False)
   phone = Column(String(20))
   store_type = Column(String(50))
   categories = Column(JSON, default=list, nullable=False)
   regions = Column(JSON, default=list, nullable=False)
   created_at = Column(DateTime, default=datetime.utcnow)
# ===== 수정 끝 =====