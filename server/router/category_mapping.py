"""
category_mapping.py
----------------------
사용자가 선택한 대분류(CS1/CS2/CS3)/중분류(실제 service_code)를 실제 존재하는
service_code 목록으로 변환. major_categories/sub_categories 테이블(DB)을 기준으로
검증하므로, 나중에 업종이 추가/변경되어도 코드 수정 없이 DB만 갱신하면 됨.

파일 위치: server/router/category_mapping.py
(직접 실행하는 파일이 아니라, recommend.py가 import해서 쓰는 헬퍼 모듈입니다.)
사전 준비: server/scripts/seed_categories.py를 한 번 실행해서
           major_categories/sub_categories 테이블을 채워둬야 함.
"""

from sqlalchemy.orm import Session

from models.category import MajorCategory, SubCategory


def resolve_primary_codes(db: Session, major_categories: list[str], sub_categories: list[str]) -> list[str]:
    """추천/비추천 순위를 매길 '주 후보군' - 사용자가 실제로 체크한 항목 그 자체.

    - sub_categories가 있으면: 체크한 그 코드들 (DB에 실존하는 것만 검증)
    - sub_categories 없이 major_categories만 있으면: 그 대분류 전체
    - 둘 다 없으면: 빈 리스트
    """
    if sub_categories:
        rows = db.query(SubCategory.code).filter(SubCategory.code.in_(sub_categories)).all()
        return sorted({row.code for row in rows})

    if major_categories:
        rows = (
            db.query(SubCategory.code)
            .join(MajorCategory, SubCategory.major_id == MajorCategory.id)
            .filter(MajorCategory.code.in_(major_categories))
            .all()
        )
        return sorted({row.code for row in rows})

    return []


def resolve_reference_pool(db: Session, major_categories: list[str], sub_categories: list[str]) -> list[str]:
    """'선택 안 했지만 참고할 업종'을 뽑을 후보군 - 관련 대분류 전체 중
    사용자가 체크하지 않은 나머지. sub_categories를 아예 안 골랐으면(대분류만 선택)
    제외할 게 없으므로 빈 리스트(참고 항목 없음)를 반환.
    """
    if not sub_categories:
        return []

    if major_categories:
        prefixes = set(major_categories)
    else:
        prefixes = {code[:3] for code in sub_categories}

    rows = (
        db.query(SubCategory.code)
        .join(MajorCategory, SubCategory.major_id == MajorCategory.id)
        .filter(MajorCategory.code.in_(prefixes))
        .all()
    )
    pool = {row.code for row in rows}
    pool -= set(sub_categories)  # 체크한 건 참고 후보에서 제외

    return sorted(pool)