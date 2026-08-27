import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import Base, engine
import models 

# from routes.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = os.getenv(
    "FRONT_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# app.include_router(auth_router, prefix="/api/auth")


@app.get("/")
def root():
    return {"message": "backend alive"}