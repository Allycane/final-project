import os
from openai import OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ⚠️ 클라이언트를 모듈 최상단(import 시점)에서 만들지 않습니다.
# 여기서 바로 OpenAI(...)를 생성하면, 이 서비스 파일을 import하는 순간(main.py 기동 시점)
# 키 누락/버전 호환성 문제 등으로 예외가 나면 FastAPI 앱 자체가 뜨지 못하고,
# 그 결과 챗봇과 무관한 회원가입/로그인 같은 페이지까지 전부 500/연결 실패가 됩니다.
# 그래서 실제로 채팅 요청이 들어왔을 때(generate_reply 호출 시점)만 생성하도록 지연시킵니다.
_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

SYSTEM_PROMPT = """\
당신은 대한민국 창업 컨설턴트 AI '스타트업 어드바이저'입니다.
사용자의 회원 프로필(관심 업종/지역/희망 매장 유형)과 실제 상권 데이터를 참고하여,
창업을 준비하는 사람에게 구체적이고 실행 가능한 조언을 제공합니다.

원칙:
1. 제공된 [회원 프로필]과 [상권 데이터] 컨텍스트에 근거해서 답변하세요.
   컨텍스트에 없는 수치는 추측해서 단정적으로 말하지 말고, "정확한 데이터가 없어
   일반적인 경향으로 말씀드리면"과 같이 명확히 구분해서 안내하세요.
2. 답변은 친절하지만 전문적인 어조로, 필요한 경우 항목을 나눠 구조적으로 설명하세요.
3. 투자/금융 조언처럼 확정적인 수익을 보장하는 표현은 피하고, 참고 정보임을 명확히 하세요.
4. 사용자의 관심 업종/지역이 프로필에도 없고 메시지에서도 파악되지 않았다면 먼저 되물어 파악하세요.
"""


def build_context_block(user_profile: dict | None, district_rows: list[dict]) -> str:
    """DB에서 조회한 회원 프로필과 상권 데이터를 프롬프트용 텍스트로 변환"""
    parts = []

    if user_profile:
        parts.append("[회원 프로필]")
        for k, v in user_profile.items():
            if v:  # 빈 리스트/None은 제외
                parts.append(f"- {k}: {v}")

    if district_rows:
        parts.append("\n[관련 상권 데이터]")
        for row in district_rows:
            parts.append(f"- {row}")

    if not parts:
        return ""

    return "\n".join(parts)


def generate_reply(history: list[dict], user_message: str, context_block: str) -> str:
    """
    history: [{"role": "user"/"assistant", "content": "..."}] 형태의 과거 대화
    context_block: DB에서 뽑아온 회원정보 + 상권 데이터 요약 텍스트
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if context_block:
        messages.append({
            "role": "system",
            "content": f"다음은 이번 대화에 참고할 실제 데이터입니다:\n\n{context_block}",
        })

    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = _get_client().chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=800,
    )

    return response.choices[0].message.content