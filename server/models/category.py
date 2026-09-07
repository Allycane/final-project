"""
업종 대분류/소분류 테이블.

users.categories 컬럼에는 sub_categories.name 값이 그대로 배열로 저장되고,
이 값은 store.service_name과 1:1로 대응됩니다 (기존에 확인된 내용).

이 모델은 챗봇 컨텍스트를 더 풍부하게 만들기 위해 소분류 -> 대분류 이름을
함께 보여주는 용도로 사용합니다 (예: "커피-음료" -> "외식업").
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database.connection import Base


class MajorCategory(Base):
    __tablename__ = "major_categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True)   # 예: "CS1"
    name = Column(String(100))                            # 예: "외식업"

    sub_categories = relationship("SubCategory", back_populates="major")


class SubCategory(Base):
    __tablename__ = "sub_categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True)    # 예: "CS100010"
    name = Column(String(100), index=True)                 # 예: "커피-음료" (= store.service_name)
    major_id = Column(Integer, ForeignKey("major_categories.id"))

    major = relationship("MajorCategory", back_populates="sub_categories")
