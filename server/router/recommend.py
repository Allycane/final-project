"""
recommend.py
--------------
Page 1 "업종 추천" 관련 FastAPI 라우터.
front/src/api/recommendationApi.js 가 기대하는 계약을 그대로 구현:
    GET  /api/regions        -> [{code, name}, ...]
    GET  /api/categories     -> [{code, name, children:[{code,name}]}, ...]
    POST /api/recommendation -> {recommended, notRecommended, reference}

실행 위치: server/router/recommend.py
main.py 에서 아래처럼 등록해서 사용:
    from router.recommend import router as recommend_router
    app.include_router(recommend_router, prefix="/api")
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from models.category import MajorCategory
from router.category_mapping import resolve_service_codes
from router.inference import build_recommendation_result

router = APIRouter()


# ── 지역 목록 (front/src/mocks/regions.js 와 동일한 서울 25개 자치구) ──
REGIONS = [
    {"code": "11680", "name": "강남구"}, {"code": "11740", "name": "강동구"},
    {"code": "11305", "name": "강북구"}, {"code": "11500", "name": "강서구"},
    {"code": "11620", "name": "관악구"}, {"code": "11215", "name": "광진구"},
    {"code": "11530", "name": "구로구"}, {"code": "11545", "name": "금천구"},
    {"code": "11350", "name": "노원구"}, {"code": "11320", "name": "도봉구"},
    {"code": "11230", "name": "동대문구"}, {"code": "11590", "name": "동작구"},
    {"code": "11440", "name": "마포구"}, {"code": "11410", "name": "서대문구"},
    {"code": "11650", "name": "서초구"}, {"code": "11200", "name": "성동구"},
    {"code": "11290", "name": "성북구"}, {"code": "11710", "name": "송파구"},
    {"code": "11470", "name": "양천구"}, {"code": "11560", "name": "영등포구"},
    {"code": "11170", "name": "용산구"}, {"code": "11380", "name": "은평구"},
    {"code": "11110", "name": "종로구"}, {"code": "11140", "name": "중구"},
    {"code": "11260", "name": "중랑구"},
]
# 카테고리는 이제 하드코딩 상수가 아니라 major_categories/sub_categories 테이블에서
# 조회함 (server/scripts/seed_categories.py로 미리 채워둬야 함). 아래 get_categories() 참고.


class RecommendationRequest(BaseModel):
    region: str
    majorCategories: list[str] = []
    subCategories: list[str] = []


@router.get("/regions")
def get_regions():
    return REGIONS


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    # relationship() 덕분에 major.sub_categories로 딸린 중분류를 바로 순회 가능
    majors = db.query(MajorCategory).order_by(MajorCategory.id).all()
    return [
        {
            "code": major.code,
            "name": major.name,
            "children": [
                {"code": sub.code, "name": sub.name} for sub in major.sub_categories
            ],
        }
        for major in majors
    ]


@router.post("/recommendation")
def post_recommendation(req: RecommendationRequest, db: Session = Depends(get_db)):
    if not req.region:
        raise HTTPException(status_code=400, detail="region은 필수입니다.")

    service_codes = resolve_service_codes(db, req.majorCategories, req.subCategories)
    if not service_codes:
        raise HTTPException(
            status_code=400,
            detail="majorCategories 또는 subCategories 중 최소 하나는 선택해야 합니다.",
        )

    try:
        district_code = int(req.region)
    except ValueError:
        raise HTTPException(status_code=400, detail="region은 자치구 코드(숫자)여야 합니다.")

    result = build_recommendation_result(district_code, service_codes)

    if result["recommended"] is None:
        raise HTTPException(
            status_code=404,
            detail="선택한 지역/업종 조합에 대한 데이터가 부족해 추천을 생성할 수 없습니다.",
        )

    return result
