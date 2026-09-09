from typing import Optional
from pydantic import BaseModel


# 프론트 mapApi.js의 getDistribution(filters)가 보내는 조건 그대로
class MapDistributionRequest(BaseModel):
    region: str
    majorCategory: Optional[str] = None
    subCategories: list[str] = []
    radius: int = 500
    centerLat: Optional[float] = None
    centerLng: Optional[float] = None
    markerLimit: Optional[int] = 30


class MapPoint(BaseModel):
    id: str
    name: str
    category: str
    lat: float
    lng: float


class MapCenter(BaseModel):
    lat: float
    lng: float


# KakaoMap.jsx가 그대로 받아서 쓰는 { center, points } 형태
class MapDistributionResponse(BaseModel):
    center: MapCenter
    points: list[MapPoint]