from sqlalchemy.orm import Session
from sqlalchemy import case

from models.user import User
from models.district import CommercialDistrict
from models.chat import ChatSession, ChatMessage
from models.category import SubCategory
from services.openai_service import generate_reply, build_context_block


def _format_quarter(year_quarter_code: int | None) -> str:
    """20261 -> '2026년 1분기'"""
    if not year_quarter_code:
        return "알 수 없음"
    year, quarter = divmod(year_quarter_code, 10)
    return f"{year}년 {quarter}분기"


def _format_won(amount: int | None) -> str:
    if amount is None:
        return "데이터 없음"
    return f"{amount:,}원"


def _row_to_dict(r: CommercialDistrict) -> dict:
    return {
        "기준분기": _format_quarter(r.year_quarter_code),
        "자치구": r.district_name,
        "업종": r.service_name,
        "업종대분류": r.service_category,
        "총 점포수": r.total_store_count,
        "개업률(%)": r.opening_rate,
        "개업 점포수": r.opening_store_count,
        "폐업률(%)": r.closing_rate,
        "폐업 점포수": r.closing_store_count,
        "월 매출액": _format_won(r.monthly_sales_amount),
        "남성 매출액": _format_won(r.male_sales_amount),
        "여성 매출액": _format_won(r.female_sales_amount),
        "데이터 유형": "실측" if r.sales_data_type == "actual" else "추정(참고용)",
    }


def get_or_create_session(db: Session, user_id: int, session_id: int | None) -> ChatSession:
    if session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
        if session:
            return session

    session = ChatSession(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def resolve_store_type_names(db: Session, names: list[str]) -> list[str]:
    """
    users.store_types에는 store_types.name 값이 그대로 배열로 저장되어 있으므로
    별도 변환 없이 그대로 사용합니다.

    (추후 store_types 테이블에 표시용 설명이나 별칭이 추가되는 경우를 대비해
     조회 지점을 서비스 레이어에 남겨두고, 지금은 patch 없이 그대로 반환합니다.)
    """
    return names or []


def enrich_categories_with_major(db: Session, categories: list[str]) -> list[str]:
    """
    users.categories에 저장된 값(= sub_categories.name = store.service_name)을
    "소분류(대분류)" 형태로 보여주기 위해 대분류 이름을 함께 조회합니다.
    예: "커피-음료" -> "커피-음료 (외식업)"

    일치하는 소분류를 찾지 못하면 원래 값을 그대로 사용합니다.
    """
    if not categories:
        return []

    rows = (
        db.query(SubCategory)
        .filter(SubCategory.name.in_(categories))
        .all()
    )
    name_to_major = {r.name: (r.major.name if r.major else None) for r in rows}

    result = []
    for c in categories:
        major_name = name_to_major.get(c)
        result.append(f"{c} ({major_name})" if major_name else c)
    return result


def build_user_profile_dict(db: Session, user: User) -> dict:
    return {
        "이름": user.name,
        "희망 매장 유형": resolve_store_type_names(db, user.store_types or []),
        "관심 업종": enrich_categories_with_major(db, user.categories or []),
        "관심 지역": user.regions,   # 자치구명 그대로 (고정 mock 목록 기준)
    }


def find_relevant_districts(
    db: Session,
    user: User,
    limit: int = 5,
) -> list[dict]:
    """
    회원의 관심 업종(categories)/관심 지역(regions) 리스트를 기준으로
    관련 상권 데이터를 조회하는 매칭 버전입니다.

    - categories는 회원가입 시 store.service_name 값 중에서 선택된 것이므로
      정확히 일치(IN)하는 값으로 조회합니다 (부분일치 X).
    - regions는 서울 25개 자치구로 고정된 목록에서 선택되고 store.district_name과
      정확히 동일한 문자열이므로 마찬가지로 정확히 일치(IN)하는 값으로 조회합니다.

    분기별로 데이터가 누적되는 구조라, 같은 (자치구, 업종) 조합에 대해서는
    가장 최신 분기(year_quarter_code) 데이터만 남기고, 동일 분기에 actual/mock이
    함께 있으면 actual(실측) 데이터를 우선합니다.
    """
    categories = user.categories or []
    regions = user.regions or []

    if not categories and not regions:
        return []

    region_filter = (
        CommercialDistrict.district_name.in_(regions) if regions else None
    )
    # categories는 회원가입 시 service_name 목록에서 그대로 선택한 값이므로
    # 부분일치가 아니라 정확히 일치(IN)하는 값으로 조회
    category_filter = (
        CommercialDistrict.service_name.in_(categories) if categories else None
    )

    # actual 데이터를 mock보다 우선 정렬하기 위한 우선순위 컬럼
    data_type_priority = case((CommercialDistrict.sales_data_type == "actual", 0), else_=1)

    def _query(filter_clause):
        return (
            db.query(CommercialDistrict)
            .filter(filter_clause)
            .order_by(CommercialDistrict.year_quarter_code.desc(), data_type_priority)
            .limit(limit * 5)  # 중복 제거를 감안해 넉넉히 조회
            .all()
        )

    rows = []
    # 1순위: 관심 지역 AND 관심 업종이 둘 다 있으면 교집합부터 시도
    if region_filter is not None and category_filter is not None:
        rows = _query(region_filter & category_filter)

    # 교집합 결과가 없거나, 둘 중 하나만 있는 경우 -> 있는 조건만으로 검색
    if not rows:
        fallback_filter = region_filter if region_filter is not None else category_filter
        if category_filter is not None and region_filter is not None:
            # 교집합이 없었을 때는 업종을 우선 기준으로 (지역보다 창업 아이템이 더 중요한 정보이므로)
            fallback_filter = category_filter
        rows = _query(fallback_filter)

    # 같은 (자치구, 업종) 조합은 가장 최신 분기(=먼저 나오는 행) 하나만 사용
    seen: set[tuple[str, str]] = set()
    unique_rows: list[CommercialDistrict] = []
    for r in rows:
        key = (r.district_name, r.service_name)
        if key in seen:
            continue
        seen.add(key)
        unique_rows.append(r)
        if len(unique_rows) >= limit:
            break

    return [_row_to_dict(r) for r in unique_rows]


def get_history_as_messages(session: ChatSession, limit: int = 20) -> list[dict]:
    """OpenAI messages 형식으로 변환 (최근 limit개만 사용해 토큰 절약)"""
    recent = session.messages[-limit:] if session.messages else []
    return [{"role": m.role, "content": m.content} for m in recent]


def save_message(db: Session, session_id: int, role: str, content: str):
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    db.commit()


def handle_chat(db: Session, user: User, session_id: int | None, user_message: str):
    session = get_or_create_session(db, user.id, session_id)

    user_profile = build_user_profile_dict(db, user)
    district_rows = find_relevant_districts(db, user)
    context_block = build_context_block(user_profile, district_rows)

    history = get_history_as_messages(session)

    reply = generate_reply(history=history, user_message=user_message, context_block=context_block)

    save_message(db, session.id, "user", user_message)
    save_message(db, session.id, "assistant", reply)

    return session.id, reply
