from sqlalchemy.orm import Session

from models.chat_history import ChatHistoryEntry
from models.user import User

MAX_ENTRIES = 3


def _entry_to_dict(entry: ChatHistoryEntry) -> dict:
    """프론트엔드가 기대하는 {id, title, savedAt, messages} 형태로 변환"""
    return {
        "id": entry.id,
        "title": entry.title,
        "savedAt": entry.saved_at,
        "messages": entry.messages,
    }


def list_entries(db: Session, user: User) -> list[dict]:
    entries = (
        db.query(ChatHistoryEntry)
        .filter(ChatHistoryEntry.user_id == user.id)
        .order_by(ChatHistoryEntry.created_at.desc())
        .limit(MAX_ENTRIES)
        .all()
    )
    return [_entry_to_dict(e) for e in entries]


def save_entry(db: Session, user: User, title: str, saved_at: str, messages: list[dict]) -> dict:
    entry = ChatHistoryEntry(user_id=user.id, title=title, saved_at=saved_at, messages=messages)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # 최대 개수(MAX_ENTRIES) 초과분은 오래된 것부터 삭제
    all_entries = (
        db.query(ChatHistoryEntry)
        .filter(ChatHistoryEntry.user_id == user.id)
        .order_by(ChatHistoryEntry.created_at.desc())
        .all()
    )
    for old_entry in all_entries[MAX_ENTRIES:]:
        db.delete(old_entry)
    if len(all_entries) > MAX_ENTRIES:
        db.commit()

    return _entry_to_dict(entry)


def delete_entry(db: Session, user: User, entry_id: int) -> bool:
    entry = (
        db.query(ChatHistoryEntry)
        .filter(ChatHistoryEntry.id == entry_id, ChatHistoryEntry.user_id == user.id)
        .first()
    )
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True