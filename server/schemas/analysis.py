from typing import Optional
from pydantic import BaseModel


# 프론트 AiAnalysis.jsx 의 handleSubmit()이 보내는 조건 그대로
class AnalysisRequest(BaseModel):
    region: str            # 자치구 (예: "강남구")
    majorCategory: str     # 업종 대분류 코드
    minorCategory: str     # 업종 소분류 코드
    targetSales: int       # 분기별 목표 매출액 (만원)


# SalesLineChart가 그리는 분기별 포인트 하나
# actual/predicted는 둘 중 하나만 값이 있고 나머지는 null (mock과 동일)
class QuarterPoint(BaseModel):
    quarter: str
    actual: Optional[int] = None
    predicted: Optional[int] = None
    target: int


# 프론트 result 전체 형태 (StatTile 4개 + 차트 + 인사이트 문구)
class AnalysisResponse(BaseModel):
    averageSales: str
    vsTarget: str
    predictedSales: str
    targetAchieveRate: str
    insight: str
    quarters: list[QuarterPoint]