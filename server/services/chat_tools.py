"""
OpenAI function calling(tool use)에 쓰이는 "도구" 정의와 실제 실행 로직입니다.

지금까지는 회원가입 때 등록한 관심 업종/지역만으로 컨텍스트를 미리 만들어서
GPT에게 넘겼습니다. 그러다 보니 사용자가 프로필에 없는 업종/지역을 채팅에서
물어보면("중식음식점 어때?") 애초에 그 데이터를 조회하지도 않아서 GPT가
"정보가 없다"고 답할 수밖에 없었습니다.

이 파일의 도구들을 GPT에게 쥐어주면, GPT가 대화 맥락상 필요하다고 판단할 때
스스로 DB를 조회해서 답변할 수 있습니다.
"""
from sqlalchemy.orm import Session
from sqlalchemy import distinct, case

from models.district import CommercialDistrict
from models.category import SubCategory
from services.ranking_service import rank_regions_for_category
from services.format_utils import row_to_dict

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_valid_categories",
            "description": (
                "창업 가능한 업종(카테고리) 전체 목록을 조회합니다. "
                "사용자가 말한 업종명이 DB에 저장된 정확한 값과 다를 수 있으므로, "
                "get_district_ranking이나 get_store_data를 호출하기 전에 먼저 이 도구로 "
                "정확한 업종명을 확인하세요."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_valid_regions",
            "description": "상권 데이터가 존재하는 서울 자치구 전체 목록을 조회합니다.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_district_ranking",
            "description": (
                "특정 업종에 대해 서울 자치구별 창업 적합도 순위(수익성/안정성/최근추세/시장여유 "
                "종합 점수)를 조회합니다. '어디에 창업하는 게 좋을지', '추천 지역이 어디인지' 같은 "
                "질문에 사용하세요. category는 get_valid_categories로 확인한 정확한 값이어야 합니다."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "정확한 업종명 (예: '커피-음료')"},
                    "top_n": {"type": "integer", "description": "상위 몇 개 지역을 볼지 (기본 5)"},
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_store_data",
            "description": (
                "특정 업종/지역 조합의 최신 상권 데이터(매출, 점포수, 개업률/폐업률 등)를 "
                "조회합니다. 순위 비교가 아니라 특정 지역 하나, 또는 특정 업종 하나에 대한 "
                "구체적인 수치가 필요할 때 사용하세요. category, region 중 최소 하나는 필요합니다."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "정확한 업종명 (예: '커피-음료')"},
                    "region": {"type": "string", "description": "정확한 자치구명 (예: '마포구')"},
                },
                "required": [],
            },
        },
    },
]


def get_valid_categories(db: Session) -> list[str]:
    rows = db.query(SubCategory.name).order_by(SubCategory.name).all()
    return [r[0] for r in rows]


def get_valid_regions(db: Session) -> list[str]:
    rows = db.query(distinct(CommercialDistrict.district_name)).order_by(CommercialDistrict.district_name).all()
    return [r[0] for r in rows]


def get_store_data(db: Session, category: str | None, region: str | None, limit: int = 5) -> list[dict]:
    if not category and not region:
        return []

    query = db.query(CommercialDistrict)
    if category:
        query = query.filter(CommercialDistrict.service_name == category)
    if region:
        query = query.filter(CommercialDistrict.district_name == region)

    data_type_priority = case((CommercialDistrict.sales_data_type == "actual", 0), else_=1)
    rows = (
        query.order_by(CommercialDistrict.year_quarter_code.desc(), data_type_priority)
        .limit(limit * 5)
        .all()
    )

    seen: set[tuple[str, str]] = set()
    unique_rows = []
    for r in rows:
        key = (r.district_name, r.service_name)
        if key in seen:
            continue
        seen.add(key)
        unique_rows.append(r)
        if len(unique_rows) >= limit:
            break

    return [row_to_dict(r) for r in unique_rows]


def execute_tool(db: Session, name: str, arguments: dict) -> dict:
    """도구 이름 + 인자를 받아 실제로 DB를 조회하고 결과를 dict로 반환합니다."""
    if name == "get_valid_categories":
        return {"categories": get_valid_categories(db)}

    if name == "get_valid_regions":
        return {"regions": get_valid_regions(db)}

    if name == "get_district_ranking":
        category = arguments.get("category")
        top_n = arguments.get("top_n") or 5
        if not category:
            return {"error": "category가 필요합니다."}
        return rank_regions_for_category(db, category, top_n=top_n)

    if name == "get_store_data":
        results = get_store_data(db, arguments.get("category"), arguments.get("region"))
        return {"결과": results} if results else {"결과": [], "안내": "해당 조건에 맞는 상권 데이터를 찾지 못했습니다."}

    return {"error": f"알 수 없는 도구입니다: {name}"}