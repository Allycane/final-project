from pydantic import BaseModel


class ChatHistoryMessageIn(BaseModel):
    """프론트엔드 messages 배열의 항목 하나 (그대로 저장했다가 그대로 돌려줌)"""
    id: int
    role: str
    text: str
    time: str


class SaveChatHistoryRequest(BaseModel):
    title: str
    savedAt: str
    messages: list[ChatHistoryMessageIn]