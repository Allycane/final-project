from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.connection import Base


class ChatSession(Base):
    """유저별 챗봇 상담 세션 (대화방 단위)"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    # ondelete="CASCADE": users.id가 삭제되면 이 세션도 DB 레벨에서 함께 삭제됨
    # (앱 코드를 거치지 않고 DB에서 직접 회원을 지워도 동작해야 하므로 DB 제약조건으로 건다)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), default="새 상담")
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        order_by="ChatMessage.id",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base):
    """세션 내 개별 메시지 (user / assistant)"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    # ondelete="CASCADE": chat_sessions.id가 삭제되면 이 메시지도 DB 레벨에서 함께 삭제됨
    session_id = Column(
        Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(String(20), nullable=False)   # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")