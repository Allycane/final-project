"""
'채팅 내역' 사이드바에 표시되는, 사용자가 페이지를 떠날 때 자동으로 저장하는
대화 스냅샷입니다.

models/chat.py의 ChatSession/ChatMessage와는 목적이 다릅니다:
- ChatSession/ChatMessage: GPT가 대화 맥락을 기억하도록 매 메시지마다 자동으로
  쌓이는 내부 로그. 개수 제한 없음.
- ChatHistoryEntry(이 모델): 프론트엔드 AiChatMain.jsx가 페이지 이탈 시점에
  "지금까지의 대화"를 통째로 스냅샷 떠서 저장하는 것. 사용자당 최대 3개까지만
  보관되고, 초과분은 오래된 것부터 자동 삭제됨 (services/chat_history_service.py).

messages 컬럼은 프론트엔드가 쓰는 형태(JSON 배열: [{id, role, text, time}, ...])를
변환 없이 그대로 저장합니다 - 조회 시 프론트가 바로 렌더링할 수 있도록 하기 위함입니다.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey

from database.connection import Base


class ChatHistoryEntry(Base):
    __tablename__ = "chat_history_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    # 프론트에서 만든 표시용 문자열을 그대로 저장 (예: "오후 3:24"). 정렬/개수 제한 판단은
    # 이 값이 아니라 서버가 기록하는 created_at을 기준으로 한다 (클라이언트 시계는 못 믿으므로).
    saved_at = Column(String(50), nullable=False)
    messages = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)