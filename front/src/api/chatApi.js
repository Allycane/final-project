import api from "./axiosInstance";

/**
 * @param {string} message
 * @param {number|null} sessionId
 * @returns {Promise<{session_id: number, reply: string}>}
 */
export async function sendMessage(message, sessionId = null) {
  const { data } = await api.post(
    "/api/chat",
    { message, session_id: sessionId },
    { timeout: 45000 }
  );
  return data; // { session_id, reply }
}

// --- 채팅 내역(사이드바) ---

export async function fetchChatHistory() {
  const { data } = await api.get("/api/chat/sessions");
  return data; // [{ id, title, created_at }, ...]
}

export async function fetchSessionMessages(sessionId) {
  const { data } = await api.get(`/api/chat/${sessionId}/history`);
  return data; // { session_id, messages: [{ role, content, created_at }, ...] }
}

export async function deleteChatHistoryEntry(sessionId) {
  await api.delete(`/api/chat/sessions/${sessionId}`);
}