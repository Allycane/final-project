from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from models.recent_selections import RecentSelection
from schemas.recent_selections import RecentSelectionCreate, RecentSelectionResponse
from router.auth import get_current_user

router = APIRouter(prefix="/api/recent-selections", tags=["recent-selections"])

MAX_ITEMS = 3


@router.get("", response_model=list[RecentSelectionResponse])
def get_recent_selections(
   feature_key: str,
   current_user: User = Depends(get_current_user),
   db: Session = Depends(get_db),
):
   return (
      db.query(RecentSelection)
      .filter(
         RecentSelection.user_id == current_user.id,
         RecentSelection.feature_key == feature_key,
      )
      .order_by(RecentSelection.created_at.desc())
      .limit(MAX_ITEMS)
      .all()
   )


@router.post("", response_model=RecentSelectionResponse)
def create_recent_selection(
   payload: RecentSelectionCreate,
   current_user: User = Depends(get_current_user),
   db: Session = Depends(get_db),
):
   # 같은 label이 이미 있으면 지우고 새로 추가 (프론트 기존 로직과 동일)
   db.query(RecentSelection).filter(
      RecentSelection.user_id == current_user.id,
      RecentSelection.feature_key == payload.feature_key,
      RecentSelection.label == payload.label,
   ).delete()

   entry = RecentSelection(
      user_id=current_user.id,
      feature_key=payload.feature_key,
      label=payload.label,
      payload=payload.payload,
   )
   db.add(entry)
   db.commit()
   db.refresh(entry)

   # MAX_ITEMS 초과분은 오래된 것부터 삭제
   old_ids = [
      row.id
      for row in db.query(RecentSelection)
      .filter(
         RecentSelection.user_id == current_user.id,
         RecentSelection.feature_key == payload.feature_key,
      )
      .order_by(RecentSelection.created_at.desc())
      .offset(MAX_ITEMS)
      .all()
   ]
   if old_ids:
      db.query(RecentSelection).filter(RecentSelection.id.in_(old_ids)).delete(
         synchronize_session=False
      )
      db.commit()

   return entry


@router.delete("/{selection_id}")
def delete_recent_selection(
   selection_id: int,
   current_user: User = Depends(get_current_user),
   db: Session = Depends(get_db),
):
   db.query(RecentSelection).filter(
      RecentSelection.id == selection_id,
      RecentSelection.user_id == current_user.id,
   ).delete()
   db.commit()
   return {"detail": "삭제되었습니다."}
