import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import Base, engine
from router.auth import router as auth_router
from router.analysis import router as analysis_router
from router.chat import router as chat_router
from router.recommend import router as recommend_router
from router.recent_selections import router as recent_selections_router
from router.inference import preload
from router.analysis_inference import load_revenue_models

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    preload()
    load_revenue_models()  # Page2(매출분석) 모델도 서버 시작 시 미리 로드
                            # (안 하면 /api/analysis 첫 요청 때 로드하느라 20초+ 걸려 프론트 타임아웃 발생)

origins = os.getenv(
    "FRONT_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(chat_router)
app.include_router(recent_selections_router)
app.include_router(recommend_router, prefix="/api")



@app.get("/")
def root():
    return {"message": "backend alive"}