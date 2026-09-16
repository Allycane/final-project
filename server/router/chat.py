from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from models.chat import ChatSession
from schemas.chat import (
    ChatRequest,
    ChatResponse,
    SessionHistoryOut,
    MessageOut,
    ChatSessionSummary,
)
from router.auth import get_current_user
from services import chat_service
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        session_id, reply = chat_service.handle_chat(
            db=db,
            user=current_user,
            session_id=req.session_id,
            user_message=req.message,
        )
    except Exception:
        # 상세 원인은 서버 로그에만 남기고, 클라이언트에는 내부 정보가 담기지
        # 않은 일반 메시지만 내려준다.
        logger.exception("챗봇 처리 중 오류 (user_id=%s, session_id=%s)", current_user.id, req.session_id)
        raise HTTPException(status_code=500, detail="챗봇 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

    return ChatResponse(session_id=session_id, reply=reply)


@router.get("/{session_id}/history", response_model=SessionHistoryOut)
def get_history(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    messages = [MessageOut.model_validate(m) for m in session.messages]
    return SessionHistoryOut(session_id=session.id, messages=messages)


# --- 사이드바 '채팅 내역' ---
# 이미 매 메시지마다 즉시 저장되는 chat_sessions/chat_messages를 그대로 사이드바
# 목록으로 사용한다 (새로고침해도 남아있고, 한 턴만 주고받아도 바로 저장됨).

@router.get("/sessions", response_model=list[ChatSessionSummary])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat_service.list_recent_sessions(db, current_user)


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = chat_service.delete_session(db, current_user, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return {"deleted": True}