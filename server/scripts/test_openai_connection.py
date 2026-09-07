"""
OpenAI API 키 연동을 앱 전체와 분리해서 빠르게 확인하기 위한 스크립트입니다.
DB 연결 없이 OpenAI 쪽만 단독으로 테스트합니다.

사용법:
    export OPENAI_API_KEY=sk-...        # 또는 .env에 넣고 python-dotenv로 로드
    python scripts/test_openai_connection.py
"""
import os
import sys

from openai import OpenAI, AuthenticationError, APIConnectionError

# .env 파일을 쓰고 있다면 자동 로드 (없어도 무시됨)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 또는 export로 설정해주세요.")
        sys.exit(1)

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    print(f"OpenAI API 연결 테스트 중... (model={model})")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "당신은 연결 테스트용 어시스턴트입니다."},
                {"role": "user", "content": "한 문장으로 인사해줘."},
            ],
            max_tokens=50,
        )
        print("✅ 연결 성공!")
        print("응답:", response.choices[0].message.content)

    except AuthenticationError:
        print("❌ 인증 실패: OPENAI_API_KEY 값이 올바른지 확인해주세요.")
        sys.exit(1)
    except APIConnectionError:
        print("❌ 네트워크 연결 실패: 인터넷 연결 또는 프록시/방화벽 설정을 확인해주세요.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 알 수 없는 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
