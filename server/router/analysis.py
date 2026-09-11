from fastapi import APIRouter, Depends  # Depends 추가 (기존: "from fastapi import APIRouter")
from sqlalchemy.orm import Session  
from database.connection import get_db 
from schemas.analysis import AnalysisRequest, AnalysisResponse, QuarterPoint
from schemas.map import MapDistributionRequest, MapDistributionResponse  
from services import map_service  

router = APIRouter(prefix="/api/analysis", tags=["ai"])

@router.post("", response_model=AnalysisResponse)
def predict_sales(payload: AnalysisRequest) -> AnalysisResponse:
   #  AI 매출 분석 엔드포인트. (이 함수는 변경 없음)

   #  TODO(모델 완성 후):
   #    1. server/ml/page2/*.pkl 로드 (joblib.load)
   #    2. payload(region/majorCategory/minorCategory/targetSales) -> 학습 때 쓴
   #       feature_engineering.py 의 인코더/피처 순서에 맞게 변환
   #    3. model.predict(...) 결과로 아래 스텁 값들을 실제 계산값으로 교체
   #    4. insight 문구도 예측 결과 기반으로 동적 생성

   #  지금은 프론트-백엔드 연결 확인 및 Swagger 문서화 목적의 더미 응답만 반환한다.
    return AnalysisResponse(
        averageSales="8,200만원",
        vsTarget="+64%",
        predictedSales="9,100만원",
        targetAchieveRate="72%",
        insight=(
            f"[임시 응답] {payload.region} / {payload.majorCategory}-{payload.minorCategory} "
            f"조건, 목표 매출 {payload.targetSales}만원 기준 - 모델 연동 전 더미 데이터입니다."
        ),
        quarters=[
            QuarterPoint(quarter="25.4", actual=7200, predicted=None, target=payload.targetSales),
            QuarterPoint(quarter="26.1", actual=8100, predicted=None, target=payload.targetSales),
            QuarterPoint(quarter="26.2", actual=7800, predicted=None, target=payload.targetSales),
            QuarterPoint(quarter="26.3", actual=8600, predicted=None, target=payload.targetSales),
            QuarterPoint(quarter="26.4", actual=None, predicted=8900, target=payload.targetSales),
            QuarterPoint(quarter="27.1", actual=None, predicted=9100, target=payload.targetSales),
        ],
    )


@router.post("/map", response_model=MapDistributionResponse)
def get_map_distribution(
    payload: MapDistributionRequest,
    db: Session = Depends(get_db),
) -> MapDistributionResponse:
    result = map_service.get_distribution(
        db=db,
        region=payload.region,
        major_category=payload.majorCategory,
        sub_categories=payload.subCategories,
        radius=payload.radius,
        center_lat=payload.centerLat,
        center_lng=payload.centerLng,
        marker_limit=payload.markerLimit,  
    )


    if result["center"] is None:
        # 조건에 맞는 좌표가 하나도 없는 경우 - 빈 목록 + 서울시청 좌표를 기본값으로 반환
        return MapDistributionResponse(center={"lat": 37.5665, "lng": 126.9780}, points=[])

    return MapDistributionResponse(**result)