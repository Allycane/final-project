from pydantic import BaseModel
from typing import Any


class RecentSelectionCreate(BaseModel):
   feature_key: str
   label: str
   payload: dict[str, Any] = {}


class RecentSelectionResponse(BaseModel):
   id: int
   label: str
   payload: dict[str, Any]

   class Config:
      from_attributes = True
