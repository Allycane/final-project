### 수정사항

## /ai-analysis, /ai-analysis/comparison
1. [수정사항 1] DB의 'store' 테이블의 "sales_data_type"의 값이 "actual"인 "업종 소분류"만 선택할 수 있도록 변경. ("sales_data_type" 컬럼의 값이 "mock"인 경우에는 목록에서 보이지 않는다.) 
단, server/router/recommend.py는 수정하지 않는다.
2. [수정사항 2] "AI 분석 매출 확인하기" 버튼 하단에 "※실측 데이터가 존재하지 않는 업종은 제외되었습니다." 문구 추가. 색상은 붉은색으로 처리.

## /ai-analysis/comparison
1. [수정사항 2] 분석 조건 설정 섹션에서 이미 선택된 "자치구" 항목이 중복으로 선택되지 않도록, 이미 선택된 "자치구"는 목록에서 비표시 처리한다.