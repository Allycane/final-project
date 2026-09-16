from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.category import MajorCategory
from models.district import CommercialDistrict
from schemas.analysis import AnalysisRequest, AnalysisResponse, QuarterPoint
from schemas.map import MapDistributionRequest, MapDistributionResponse
from services import map_service
from router.analysis_inference import build_analysis_result
from router.recommend import REGIONS

router = APIRouter(prefix="/api/analysis", tags=["ai"])

# region이 프론트에서 코드("11680")로 오는지 이름("강남구")으로 오는지 확정하기 전까지
# 둘 다 안전하게 처리하기 위한 이름 -> 코드 매핑 (Page1의 REGIONS 재사용)
_NAME_TO_CODE = {r["name"]: r["code"] for r in REGIONS}


def _resolve_district_code(region: str) -> str:
    """region이 이미 코드(숫자 문자열)면 그대로, 이름이면 코드로 변환."""
    if region.isdigit():
        return region
    return _NAME_TO_CODE.get(region, region)


@router.get("/categories")
def get_actual_categories(db: Session = Depends(get_db)):
    """AI 매출 분석 전용 업종 목록 - store 테이블에 sales_data_type="actual"인
    행이 하나라도 있는 업종(소분류)만 남긴다. (recommend.py의 /api/categories는
    Page1 추천에서 계속 전체 업종을 써야 하므로 건드리지 않고 별도 엔드포인트로 분리)"""
    actual_service_codes = {
        row[0]
        for row in db.query(CommercialDistrict.service_code)
        .filter(CommercialDistrict.sales_data_type == "actual")
        .distinct()
        .all()
    }

    majors = db.query(MajorCategory).order_by(MajorCategory.id).all()
    result = []
    for major in majors:
        children = [
            {"code": sub.code, "name": sub.name}
            for sub in major.sub_categories
            if sub.code in actual_service_codes
        ]
        if children:
            result.append({"code": major.code, "name": major.name, "children": children})

    return result


@router.post("", response_model=AnalysisResponse)
def predict_sales(payload: AnalysisRequest, db: Session = Depends(get_db)) -> AnalysisResponse:
    """AI 매출 분석 엔드포인트 - 실제 RandomForest 모델 기반 예측.
    (더미 응답 -> 실제 로직으로 교체됨. /map 엔드포인트는 팀원 작업 그대로 유지)"""
    district_code = _resolve_district_code(payload.region)

    result = build_analysis_result(
        db=db,
        district_code=district_code,
        service_code=payload.minorCategory,
        target_sales_manwon=payload.targetSales,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="선택한 지역/업종 조합에 대한 데이터가 부족해 분석을 생성할 수 없습니다.",
        )

    return AnalysisResponse(
        averageSales=result["averageSales"],
        vsTarget=result["vsTarget"],
        predictedSales=result["predictedSales"],
        targetAchieveRate=result["targetAchieveRate"],
        insight=result["insight"],
        quarters=[QuarterPoint(**q) for q in result["quarters"]],
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
