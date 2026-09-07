from typing import Optional
from pydantic import BaseModel


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

    class Config:
        from_attributes = True


class ChatSessionOut(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class SessionHistoryOut(BaseModel):
    session_id: int
    messages: list[MessageOut]
