from fastapi import APIRouter

from schemas.analysis import AnalysisRequest, AnalysisResponse, QuarterPoint

# auth 라우터(/api/auth) 컨벤션에 맞춤.
# axiosInstance가 baseURL(http://localhost:8000)로 FastAPI에 직접 요청하므로
# vite.config.js의 "/predict" 프록시와는 무관함 (그 프록시는 현재 미사용 경로).
router = APIRouter(prefix="/api/analysis", tags=["ai"])


@router.post("", response_model=AnalysisResponse)
def predict_sales(payload: AnalysisRequest) -> AnalysisResponse:
   #  AI 매출 분석 엔드포인트.

   #  TODO(모델 완성 후):
   #    1. server/ml/page2/*.pkl 로드 (joblib.load)
   #    2. payload(region/majorCategory/minorCategory/targetSales) -> 학습 때 쓴
   #       feature_engineering.py 의 인코더/피처 순서에 맞게 변환
   #    3. model.predict(...) 결과로 아래 스텁 값들을 실제 계산값으로 교체
   #    4. insight 문구도 예측 결과 기반으로 동적 생성

   #  지금은 프론트-백엔드 연결 확인 및 Swagger 문서화 목적의 더미 응답만 반환한다.
    return AnalysisResponse(
        averageSales="8,200만원",
        vsTarget="+64%",
        predictedSales="9,100만원",
        targetAchieveRate="72%",
        insight=(
            f"[임시 응답] {payload.region} / {payload.majorCategory}-{payload.minorCategory} "
            f"조건, 목표 매출 {payload.targetSales}만원 기준 - 모델 연동 전 더미 데이터입니다."
        ),
        quarters=[
            QuarterPoint(quarter="25.4", actual=7200, predicted=None, target=payload.targetSales),
            QuarterPoint(quarter="26.1", actual=8100, predicted=None, target=payload.targetSales),
            QuarterPoint(quarter="26.2", actual=7800, predicted=None, target=payload.targetSales),
            QuarterPoint(quarter="26.3", actual=8600, predicted=None, target=payload.targetSales),
            QuarterPoint(quarter="26.4", actual=None, predicted=8900, target=payload.targetSales),
            QuarterPoint(quarter="27.1", actual=None, predicted=9100, target=payload.targetSales),
        ],
    )