"""
services/chat_service.py, services/chat_tools.py 양쪽에서 공통으로 쓰는
상권 데이터 포맷팅 헬퍼입니다. 두 파일이 서로를 import하지 않도록
공통 로직만 이 파일로 분리했습니다.
"""
from models.district import CommercialDistrict


def format_quarter(year_quarter_code: int | None) -> str:
    """20261 -> '2026년 1분기'"""
    if not year_quarter_code:
        return "알 수 없음"
    year, quarter = divmod(year_quarter_code, 10)
    return f"{year}년 {quarter}분기"


def format_won(amount: int | None) -> str:
    if amount is None:
        return "데이터 없음"
    return f"{amount:,}원"


def row_to_dict(r: CommercialDistrict) -> dict:
    return {
        "기준분기": format_quarter(r.year_quarter_code),
        "자치구": r.district_name,
        "업종": r.service_name,
        "업종대분류": r.service_category,
        "총 점포수": r.total_store_count,
        "개업률(%)": r.opening_rate,
        "개업 점포수": r.opening_store_count,
        "폐업률(%)": r.closing_rate,
        "폐업 점포수": r.closing_store_count,
        "월 매출액": format_won(r.monthly_sales_amount),
        "남성 매출액": format_won(r.male_sales_amount),
        "여성 매출액": format_won(r.female_sales_amount),
        "데이터 유형": "실측" if r.sales_data_type == "actual" else "추정(참고용)",
    }