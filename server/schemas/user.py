from pydantic import BaseModel, EmailStr
from typing import Optional


class SignupBasicRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None


class SignupInterestsRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    categories: list[str] = []
    regions: list[str] = []
    storeType: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# 마이페이지가 로그인/조회 응답에서 이 값을 그대로 쓸 수 있게 함.
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: Optional[str] = None
    store_type: Optional[str] = None
    categories: list[str] = []
    regions: list[str] = []

    class Config:
        from_attributes = True

# 
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    categories: Optional[list[str]] = None
    regions: Optional[list[str]] = None
    store_types: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

