import { mockBotReply } from "../mocks/chatMessages";

export async function sendMessage(message) {
  // TODO: FastAPI/LLM 연동 - axiosInstance의 api를 import해서 실제 엔드포인트로 교체
  // import api from "./axiosInstance";
  // const { data } = await api.post("/api/chat", { message });
  // return data;
  console.debug("[mock] sendMessage message:", message);

  return new Promise((resolve) =>
    setTimeout(() => resolve({ ...mockBotReply, id: Date.now() }), 500)
  );
}
