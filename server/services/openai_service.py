import json
import os
from openai import OpenAI
from sqlalchemy.orm import Session

from services.chat_tools import TOOL_DEFINITIONS, execute_tool

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_TOOL_ITERATIONS = 4  # 도구 호출이 무한 반복되지 않도록 상한선

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
사용자의 회원 프로필(관심 업종/지역/희망 매장 유형)과 실제 상권 데이터, 그리고
업종별 자치구 순위 분석 결과를 참고하여, 창업을 준비하는 사람에게 구체적이고
실행 가능한 조언을 제공합니다.

당신은 아래 도구(tool)들을 사용해 DB에서 직접 데이터를 조회할 수 있습니다:
- get_valid_categories / get_valid_regions: 정확한 업종명/지역명 목록 확인
- get_district_ranking: 특정 업종의 자치구별 창업 적합도 순위 조회
- get_store_data: 특정 업종/지역의 구체적인 상권 수치 조회

원칙:
1. 아래에 미리 제공된 [회원 프로필], [관련 상권 데이터], [업종별 지역 추천 순위]는
   사용자가 회원가입 때 등록한 관심사를 기준으로 미리 계산해둔 참고 자료입니다.
2. **사용자가 미리 제공된 컨텍스트에 없는 업종이나 지역을 물어보면, "데이터가 없다"고
   바로 답하지 말고 반드시 도구를 사용해서 실제로 조회한 뒤에 답변하세요.** 업종명은
   사용자가 말한 표현과 DB의 정확한 명칭이 다를 수 있으니, get_valid_categories로
   먼저 정확한 값을 확인한 다음 get_district_ranking이나 get_store_data를 호출하세요.
   (예: 사용자가 "중식집"이라고 말해도 DB에는 "중식음식점"으로 저장되어 있을 수 있습니다.)
3. 도구로 조회해봤는데도 진짜 데이터가 없을 때만 "해당 데이터는 없다"고 안내하세요.
4. **절대로 도구가 반환한 원본 데이터(딕셔너리, 필드명, 점수 라벨 등)를 그대로 베껴서
   나열하지 마세요.** "종합점수: 70.5", "수익성 점수: 100.0 (점포당 월 매출:
   62,471,230원)" 같은 항목별 리스트 형태는 절대 쓰지 마세요. 대신 숫자를 근거로
   자연스러운 문장으로 풀어서 설명하세요.

   나쁜 예 (절대 이렇게 쓰지 마세요):
   "1. 종로구
   - 종합점수: 70.5
   - 수익성 점수: 100.0 (점포당 월 매출: 62,471,230원)
   - 안정성 점수: 70.9 (개업률 - 폐업률: -1.3%)"

   좋은 예 (이런 식으로 서술하세요):
   "종로구가 가장 눈에 띕니다. 점포당 월매출이 약 6,247만원으로 조사된 지역 중
   가장 높아서 수익성 면에서는 확실한 강점이 있어요. 다만 폐업률이 개업률보다
   1.3%p 높은 편이라 안정성은 보통 수준이고, 최근 매출 성장세도 거의 정체(+0.4%)
   돼 있어서 '이미 자리 잡은 안정적인 상권'에 가깝습니다."

5. 여러 지역을 비교할 때는 상위 1~2곳은 위 예시처럼 자세히 설명하고, 나머지는
   "그 다음으로는 서초구가 근소한 차이로 뒤를 잇는데, 안정성은 더 좋지만 수익성은
   다소 낮은 편이에요"처럼 짧게 비교하는 식으로 마무리하세요. 모든 지역을 똑같은
   길이로 나열하면 답변이 너무 길어져 잘릴 수 있으니 분량을 조절하세요.
6. 순위의 "최근추세" 점수가 null이면 "최근 추세는 데이터가 부족해 판단하지 않았다"고
   솔직하게 안내하세요. 임의로 추세를 지어내지 마세요.
7. "성별매출_참고" 정보는 순위를 매기는 데 쓰인 게 아니라 참고용입니다. 사용자가
   준비 중인 아이템의 주 타겟과 연결지어 설명할 때만 자연스럽게 활용하세요.
8. 답변은 친절하지만 전문적인 어조로, 마지막엔 "그래서 결론적으로 어디를 추천하는지"
   한두 문장으로 명확히 정리하세요.
9. 투자/금융 조언처럼 확정적인 수익을 보장하는 표현은 피하고, 참고 정보임을 명확히 하세요.
10. 사용자의 관심 업종/지역이 프로필에도 없고 메시지에서도 파악되지 않았다면 먼저 되물어 파악하세요.
"""


def build_context_block(
    user_profile: dict | None,
    district_rows: list[dict],
    category_rankings: list[dict] | None = None,
) -> str:
    """DB에서 조회한 회원 프로필 + 상권 데이터 + 업종별 지역 순위를 프롬프트용 텍스트로 변환"""
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

    if category_rankings:
        parts.append(
            "\n[업종별 지역 추천 순위] "
            "(가중치: 수익성 35% + 안정성 35% + 최근추세 15% + 시장여유 15%, "
            "실측 데이터만 사용, 최근추세는 2021~2022년 제외하고 계산)"
        )
        for ranking in category_rankings:
            category = ranking.get("업종")
            results = ranking.get("결과") or []
            if not results:
                parts.append(f"- {category}: {ranking.get('안내', '데이터 없음')}")
                continue
            parts.append(f"- 업종 '{category}' 추천 지역 순위:")
            for item in results:
                parts.append(f"  - {item}")

    if not parts:
        return ""

    return "\n".join(parts)


def _build_messages(context_block: str, history: list[dict], user_message: str) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if context_block:
        messages.append({
            "role": "system",
            "content": f"다음은 이번 대화에 미리 참고할 수 있는 데이터입니다:\n\n{context_block}",
        })

    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages


def generate_reply(db: Session, history: list[dict], user_message: str, context_block: str) -> str:
    """
    db: 도구(get_district_ranking 등)가 실제 DB를 조회할 때 사용
    history: [{"role": "user"/"assistant", "content": "..."}] 형태의 과거 대화
    context_block: DB에서 미리 뽑아둔 회원정보 + 상권 데이터 + 순위 요약 텍스트
    """
    messages = _build_messages(context_block, history, user_message)
    client = _get_client()

    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            temperature=0.5,
            max_tokens=1200,
        )
        message = response.choices[0].message

        # 모델이 도구 호출 없이 바로 답변했다면 그대로 반환
        if not message.tool_calls:
            return message.content

        # 모델이 도구 호출을 요청함 -> 실제로 실행하고 결과를 대화에 추가한 뒤 다시 물어봄
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [tc.model_dump() for tc in message.tool_calls],
        })

        for tool_call in message.tool_calls:
            try:
                arguments = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}

            result = execute_tool(db, tool_call.function.name, arguments)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False, default=str),
            })

    # 도구 호출 한도를 넘어서도 최종 답변이 안 나온 경우를 위한 안전장치
    return "죄송해요, 지금은 답변을 정리하는 데 어려움이 있어요. 질문을 조금 더 구체적으로 다시 해주시겠어요?"