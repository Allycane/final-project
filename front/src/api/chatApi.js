import api from "./axiosInstance";

/**
 * @param {string} message - 사용자가 입력한 메시지
 * @param {number|null} sessionId - 이어지는 대화면 이전 응답의 session_id, 첫 메시지면 null
 * @returns {Promise<{session_id: number, reply: string}>}
 */
export async function sendMessage(message, sessionId = null) {
  const { data } = await api.post("/api/chat", {
    message,
    session_id: sessionId,
  });
  return data; 
}
