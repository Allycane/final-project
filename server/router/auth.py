from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from database.connection import get_db
from models.user import User
from schemas.user import (
   SignupBasicRequest,
   SignupInterestsRequest,
   LoginRequest,
   TokenResponse,
   UserResponse,
   UpdateProfileRequest,  # 추가
)
from core.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 새로고침 시 프론트가 들고 있는 토큰으로 "지금 로그인한 사람이 누구인지"
# 서버에 물어볼 수 있도록 get_current_user 의존성과 /me 엔드포인트를 추가함
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
   if not token:
      raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
   payload = decode_access_token(token)
   if not payload:
      raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
   user = db.query(User).filter(User.id == int(payload["sub"])).first()
   if not user:
      raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
   return user


@router.post("/signup/basic")
def signup_basic(payload: SignupBasicRequest, db: Session = Depends(get_db)):
   existing = db.query(User).filter(User.email == payload.email).first()
   if existing:
      raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")
   return payload


@router.post("/signup/interests", response_model=TokenResponse)
def signup_interests(payload: SignupInterestsRequest, db: Session = Depends(get_db)):
   existing = db.query(User).filter(User.email == payload.email).first()
   if existing:
      raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")

   # JSON 리스트로 저장
   # 이제는 categories/regions를 User 객체의 컬럼값으로 바로 대입하면 됨
   user = User(
      email=payload.email,
      password_hash=hash_password(payload.password),
      name=payload.name,
      phone=payload.phone,
      store_types=payload.storeTypes,
      categories=payload.categories,
      regions=payload.regions,
   )
   db.add(user)
   db.commit()
   db.refresh(user)


   token = create_access_token({"sub": str(user.id)})
   return TokenResponse(access_token=token, user=user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
   user = db.query(User).filter(User.email == payload.email).first()
   if not user or not verify_password(payload.password, user.password_hash):
      raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

   token = create_access_token({"sub": str(user.id)})
   return TokenResponse(access_token=token, user=user)


# 로그인 유지 + 마이페이지 실제 데이터 연동용 엔드포인트
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
   return current_user



@router.post("/me/update", response_model=UserResponse)
def update_me(
   payload: UpdateProfileRequest,
   current_user: User = Depends(get_current_user),
   db: Session = Depends(get_db),
):
   if payload.email is not None and payload.email != current_user.email:
      existing = db.query(User).filter(User.email == payload.email).first()
      if existing:
         raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")
      current_user.email = payload.email

   if payload.name is not None:
      current_user.name = payload.name
   if payload.phone is not None:
      current_user.phone = payload.phone
   if payload.password:
      current_user.password_hash = hash_password(payload.password)
   if payload.categories is not None:
      current_user.categories = payload.categories
   if payload.regions is not None:
      current_user.regions = payload.regions
   if payload.store_types is not None:
      current_user.store_types = payload.store_types

   db.commit()
   db.refresh(current_user)
   return current_user
