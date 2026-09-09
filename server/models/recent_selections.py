from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from datetime import datetime
from database.connection import Base


class RecentSelection(Base):
   __tablename__ = "recent_selections"

   id = Column(Integer, primary_key=True, index=True)
   user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
   # 프론트 useRecentSelections(storageKey)의 storageKey와 동일한 값
   # recentSelections:ai-analysis 등 페이지를 그대로 저장해 페이지별로 구분
   feature_key = Column(String(100), nullable=False, index=True)
   label = Column(String(255), nullable=False)
   payload = Column(JSON, default=dict)  # 재조회 시 폼을 복원할 값들
   created_at = Column(DateTime, default=datetime.utcnow)