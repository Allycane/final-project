from passlib.context import CryptContext
import bcrypt
import os
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

ACCESS_SECRET = os.getenv("ACCESS_SECRET", "dev-access-secret")
REFRESH_SECRET = os.getenv("REFRESH_SECRET", "dev-refresh-secret")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(raw_password : str, hashed_password : str):
    return bcrypt.checkpw(raw_password.encode(), hashed_password.encode())

# token return 형식 : HEX 256 타입으로 토큰 생성 후 리턴
def _create_token(member_id : str, role : str, secret : str, expires_delta : timedelta) -> str:
    payload = {
        "sub" : member_id,
        "role" : role,
        "exp" : datetime.now(timezone.utc) + expires_delta,
    }
    return {
        jwt.encode(payload, secret, algorithm = "HS256")
    }


# access_token
def create_access_token(member_id : str, role : str) -> str:
    return _create_token(
        member_id,
        role,
        ACCESS_SECRET,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

# refresh_token
def create_refresh_token(member_id : str, role : str) -> str:
    return _create_token(
        member_id,
        role,
        REFRESH_SECRET,
        timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS)
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/member/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    accessToken을 검증하고, 토큰에 담긴 sub(=nickname)와 role을 반환하는 의존성 함수.
    보호가 필요한 라우터에서 Depends(get_current_user) 형태로 사용한다.
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
        )

    try:
        payload = jwt.decode(token, ACCESS_SECRET, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 토큰입니다.",
        )

    nickname = payload.get("sub")
    role = payload.get("role")

    if nickname is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
        )

    return {"nickname": nickname, "role": role}