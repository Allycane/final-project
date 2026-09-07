"""
seed_categories.py
---------------------
major_categories / sub_categories 테이블에 실제 업종 데이터(3개 대분류, 100개
중분류)를 채워 넣는 시딩 스크립트. categories.js와 검증 완료된 동일한 데이터 사용.

실행 위치: server/scripts/seed_categories.py
실행 방법: python seed_categories.py
    (여러 번 실행해도 안전 - 이미 있는 code는 건너뜀)
"""

import os
import sys

# server/ 를 경로에 추가해서 database, models 패키지를 절대경로로 import 가능하게 함
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from database.connection import Base, engine, SessionLocal
from models.category import MajorCategory, SubCategory

CATEGORY_DATA = [
    {"code": "CS1", "name": "외식업", "children": [
        ("CS100001", "한식음식점"), ("CS100002", "중식음식점"), ("CS100003", "일식음식점"),
        ("CS100004", "양식음식점"), ("CS100005", "제과점"), ("CS100006", "패스트푸드점"),
        ("CS100007", "치킨전문점"), ("CS100008", "분식전문점"), ("CS100009", "호프-간이주점"),
        ("CS100010", "커피-음료"),
    ]},
    {"code": "CS2", "name": "서비스업", "children": [
        ("CS200001", "일반교습학원"), ("CS200002", "외국어학원"), ("CS200003", "예술학원"),
        ("CS200004", "컴퓨터학원"), ("CS200005", "스포츠 강습"), ("CS200006", "일반의원"),
        ("CS200007", "치과의원"), ("CS200008", "한의원"), ("CS200009", "동물병원"),
        ("CS200010", "변호사사무소"), ("CS200011", "변리사사무소"), ("CS200012", "법무사사무소"),
        ("CS200013", "기타법무서비스"), ("CS200014", "회계사사무소"), ("CS200015", "세무사사무소"),
        ("CS200016", "당구장"), ("CS200017", "골프연습장"), ("CS200018", "볼링장"),
        ("CS200019", "PC방"), ("CS200020", "전자게임장"), ("CS200021", "기타오락장"),
        ("CS200022", "복권방"), ("CS200023", "통신기기수리"), ("CS200024", "스포츠클럽"),
        ("CS200025", "자동차수리"), ("CS200026", "자동차미용"), ("CS200027", "모터사이클수리"),
        ("CS200028", "미용실"), ("CS200029", "네일숍"), ("CS200030", "피부관리실"),
        ("CS200031", "세탁소"), ("CS200032", "가전제품수리"), ("CS200033", "부동산중개업"),
        ("CS200034", "여관"), ("CS200035", "게스트하우스"), ("CS200036", "고시원"),
        ("CS200037", "노래방"), ("CS200038", "독서실"), ("CS200039", "DVD방"),
        ("CS200040", "녹음실"), ("CS200041", "사진관"), ("CS200042", "통번역서비스"),
        ("CS200043", "건축물청소"), ("CS200044", "여행사"), ("CS200045", "비디오/서적임대"),
        ("CS200046", "의류임대"), ("CS200047", "가정용품임대"),
    ]},
    {"code": "CS3", "name": "도·소매업", "children": [
        ("CS300001", "슈퍼마켓"), ("CS300002", "편의점"), ("CS300003", "컴퓨터및주변장치판매"),
        ("CS300004", "핸드폰"), ("CS300005", "주류도매"), ("CS300006", "미곡판매"),
        ("CS300007", "육류판매"), ("CS300008", "수산물판매"), ("CS300009", "청과상"),
        ("CS300010", "반찬가게"), ("CS300011", "일반의류"), ("CS300012", "한복점"),
        ("CS300013", "유아의류"), ("CS300014", "신발"), ("CS300015", "가방"),
        ("CS300016", "안경"), ("CS300017", "시계및귀금속"), ("CS300018", "의약품"),
        ("CS300019", "의료기기"), ("CS300020", "서적"), ("CS300021", "문구"),
        ("CS300022", "화장품"), ("CS300023", "미용재료"), ("CS300024", "운동/경기용품"),
        ("CS300025", "자전거 및 기타운송장비"), ("CS300026", "완구"), ("CS300027", "섬유제품"),
        ("CS300028", "화초"), ("CS300029", "애완동물"), ("CS300030", "중고가구"),
        ("CS300031", "가구"), ("CS300032", "가전제품"), ("CS300033", "철물점"),
        ("CS300034", "악기"), ("CS300035", "인테리어"), ("CS300036", "조명용품"),
        ("CS300037", "중고차판매"), ("CS300038", "자동차부품"), ("CS300039", "모터사이클및부품"),
        ("CS300040", "재생용품 판매점"), ("CS300041", "예술품"), ("CS300042", "주유소"),
        ("CS300043", "전자상거래업"),
    ]},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        major_count = 0
        sub_count = 0

        for group in CATEGORY_DATA:
            major = db.query(MajorCategory).filter(MajorCategory.code == group["code"]).first()
            if not major:
                major = MajorCategory(code=group["code"], name=group["name"])
                db.add(major)
                db.flush()  # major.id를 바로 쓰기 위해 flush (commit 전에 id 확보)
                major_count += 1

            for code, name in group["children"]:
                existing = db.query(SubCategory).filter(SubCategory.code == code).first()
                if not existing:
                    db.add(SubCategory(code=code, name=name, major_id=major.id))
                    sub_count += 1

        db.commit()
        print(f"[seed] 새로 추가된 대분류: {major_count}개, 중분류: {sub_count}개")

        total_major = db.query(MajorCategory).count()
        total_sub = db.query(SubCategory).count()
        print(f"[seed] 전체 현황 - 대분류: {total_major}개, 중분류: {total_sub}개")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
