"""
store_types 참고 테이블.

확인 결과 users.store_types 컬럼에는 이 테이블의 name 값이 그대로 배열로 저장됩니다
(예: users.store_types = ["길거리 매장", "프랜차이즈"]). 따라서 챗봇 컨텍스트를 만들 때는
별도 변환이 필요 없습니다 (services/chat_service.py의 resolve_store_type_names 참고).

이 모델 자체는 회원가입 폼의 선택지 검증, 관리자 페이지 등 다른 곳에서 store_types 테이블을
조회해야 할 때 사용할 수 있어 남겨둡니다.
"""
from sqlalchemy import Column, Integer, String

from database.connection import Base


class StoreType(Base):
    __tablename__ = "store_types"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True)   # 예: "street"
    name = Column(String(100))                            # 예: "길거리 매장"
