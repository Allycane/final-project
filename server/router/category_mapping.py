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


def resolve_service_codes(db: Session, major_categories: list[str], sub_categories: list[str]) -> list[str]:
    """사용자가 선택한 대분류/중분류를 DB 기준으로 검증된 service_code 목록으로 변환.

    - sub_categories가 있으면: DB에 실제 존재하는 코드만 걸러서 반환
    - sub_categories 없이 major_categories만 있으면: 그 대분류에 속한 중분류 전체 코드 반환
    - 둘 다 없으면: 빈 리스트
    """
    if sub_categories:
        rows = (
            db.query(SubCategory.code)
            .filter(SubCategory.code.in_(sub_categories))
            .all()
        )
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
