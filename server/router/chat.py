from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from models.chat import ChatSession
from schemas.chat import ChatRequest, ChatResponse, SessionHistoryOut, MessageOut
from router.auth import get_current_user
from services import chat_service

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
    except Exception as e:
        # 운영환경에서는 상세 메시지를 그대로 노출하지 말고 로깅 후 일반 메시지 반환 권장
        raise HTTPException(status_code=500, detail=f"챗봇 처리 중 오류: {e}")

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
