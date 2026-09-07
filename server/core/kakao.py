import os
import requests
from fastapi import HTTPException

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")


def get_kakao_access_token(code: str) -> str:
    """프론트에서 받은 인가 코드(code)를 카카오 access_token으로 교환"""
    response = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": KAKAO_CLIENT_ID,
            "redirect_uri": KAKAO_REDIRECT_URI,
            "code": code,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        timeout=5,
    )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="카카오 인증에 실패했습니다.")
    return response.json()["access_token"]


def get_kakao_user_info(kakao_access_token: str) -> dict:
    """카카오 access_token으로 사용자 정보(고유 ID, 이메일, 닉네임) 조회"""
    response = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {kakao_access_token}"},
        timeout=5,
    )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="카카오 사용자 정보 조회에 실패했습니다.")

    data = response.json()
    kakao_account = data.get("kakao_account", {})
    profile = kakao_account.get("profile", {})

    return {
        "kakao_id": str(data["id"]),
        # 이메일 동의를 안 했으면 None일 수 있으므로 호출부에서 fallback 처리
        "email": kakao_account.get("email"),
        "name": profile.get("nickname", "카카오사용자"),
    }