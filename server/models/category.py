from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class MajorCategory(Base):
    """업종 대분류 (외식업/서비스업/도소매업). code는 CS1/CS2/CS3."""
    __tablename__ = "major_categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)

    # 1(대분류) : N(중분류) 관계. 대분류 하나 삭제되면 딸린 중분류도 같이 삭제(cascade)
    sub_categories = relationship(
        "SubCategory", back_populates="major", cascade="all, delete-orphan"
    )


class SubCategory(Base):
    """업종 중분류 (실제 세부 업종). code는 실제 service_code(CS100001 등)와 동일."""
    __tablename__ = "sub_categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    major_id = Column(Integer, ForeignKey("major_categories.id"), nullable=False)

    # N(중분류) : 1(대분류) 관계. sub.major 로 소속 대분류에 바로 접근 가능
    major = relationship("MajorCategory", back_populates="sub_categories")
