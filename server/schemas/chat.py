from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_serializer


def _serialize_utc(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


class ChatRequest(BaseModel):
    # user_id는 받지 않음 - JWT(get_current_user)로 로그인된 사용자 식별
    session_id: Optional[int] = None   # 없으면 새 세션 생성
    message: str


class ChatResponse(BaseModel):
    session_id: int
    reply: str


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    @field_serializer("created_at")
    def _serialize_created_at(self, dt: datetime, _info) -> str:
        return _serialize_utc(dt)

    class Config:
        from_attributes = True


class ChatSessionOut(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class ChatSessionSummary(BaseModel):
    """사이드바 '채팅 내역' 목록에 쓰이는 요약 정보 (메시지 전체는 포함하지 않음)"""
    id: int
    title: str
    created_at: datetime

    @field_serializer("created_at")
    def _serialize_created_at(self, dt: datetime, _info) -> str:
        return _serialize_utc(dt)

    class Config:
        from_attributes = True


class SessionHistoryOut(BaseModel):
    session_id: int
    messages: list[MessageOut]