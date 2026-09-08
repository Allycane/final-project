import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { sendMessage } from "../api/chatApi.js";
import { mockInitialMessages, mockQuickReplies } from "../mocks/chatMessages.js";
import { useAuth } from "../hooks/useAuth.js";
import { mockUser } from "../mocks/users.js";
import { formatChatTime } from "../utils/time.js";
import ChatBubble from "../components/chat/ChatBubble.jsx";
import Card from "../components/common/Card.jsx";
import Button from "../components/common/Button.jsx";
import Tag from "../components/common/Tag.jsx";
import "../styles/Chat.css";

const CHAT_HISTORY_KEY = "chatHistory:ai-chat-main";
const MAX_CHAT_HISTORY = 3;

// TODO: FastAPI 연동 - 지금은 채팅 내역을 브라우저 localStorage에만 저장한다.
// 로그인한 사용자의 DB에 저장하려면 아래처럼 axiosInstance의 api를 사용해
// 사용자 ID 기준으로 조회/저장하는 함수로 교체하고, 이 파일 아래쪽의
// readChatHistory() 호출부(조회)와 unmount 시 저장하는 부분(저장)을
// 각각 이 함수들로 바꿔주면 된다.
// import api from "../api/axiosInstance.js";
//
// async function fetchChatHistory(userId) {
//   // GET /api/chat/history?user_id={userId} -> 최근 3개의 대화 내역 반환
//   const { data } = await api.get("/api/chat/history", { params: { user_id: userId } });
//   return data; // [{ id, title, savedAt, messages }, ...]
// }
//
// async function saveChatHistoryEntry(userId, entry) {
//   // POST /api/chat/history -> 사용자별로 최대 3개까지만 저장하고,
//   // 초과분은 가장 오래된 대화부터 서버(DB)에서 삭제하도록 백엔드에서 처리
//   await api.post("/api/chat/history", { user_id: userId, ...entry });
// }

function readChatHistory() {
  try {
    const raw = localStorage.getItem(CHAT_HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function AiChatMain() {
  const navigate = useNavigate();
  const { user, isLoggedIn } = useAuth();
  const interests = user?.interests ?? mockUser.interests;

  const goToInfoEdit = () => navigate(isLoggedIn ? "/mypage" : "/login");

  const [messages, setMessages] = useState(() =>
    mockInitialMessages.map((message) => ({ ...message, time: formatChatTime() })),
  );
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  // 백엔드가 대화 맥락을 유지하는 기준값. 첫 메시지는 null로 보내고,
  // 이후 응답으로 받은 session_id를 계속 재사용해야 같은 대화로 이어집니다.
  const [sessionId, setSessionId] = useState(null);
  const [chatHistory] = useState(() => readChatHistory());
  // TODO: FastAPI 연동 - 위 localStorage 조회 대신 로그인한 사용자의 DB 데이터를 불러오려면
  // 아래처럼 파일 상단의 fetchChatHistory()를 사용해 마운트 시 서버에서 조회하도록 교체한다.
  // const [chatHistory, setChatHistory] = useState([]);
  // useEffect(() => {
  //   if (!user) return;
  //   fetchChatHistory(user.id).then(setChatHistory);
  // }, [user]);

  // 페이지를 벗어날 때, 실제로 대화가 오간 경우에만 채팅 내역에 저장한다.
  const messagesRef = useRef(messages);
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  useEffect(() => {
    return () => {
      const finishedMessages = messagesRef.current;
      if (finishedMessages.length <= 1) return;

      const firstUserMessage = finishedMessages.find((message) => message.role === "user");
      const entry = {
        id: Date.now(),
        title: firstUserMessage?.text.slice(0, 24) ?? "대화 내역",
        savedAt: formatChatTime(),
        messages: finishedMessages,
      };
      const next = [entry, ...readChatHistory()].slice(0, MAX_CHAT_HISTORY);
      localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(next));
      // TODO: FastAPI 연동 - 위 localStorage 저장 대신(또는 함께) 사용자 ID 기준으로
      // 서버 DB에도 저장하려면 파일 상단의 saveChatHistoryEntry()를 사용한다.
      // if (user) {
      //   saveChatHistoryEntry(user.id, entry);
      // }
    };
  }, []);

  const restoreConversation = (entry) => {
    setMessages(entry.messages);
    setSessionId(null);
  };

  const appendUserMessage = (text) => {
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), role: "user", text, time: formatChatTime() },
    ]);
  };

  const appendBotMessage = (text) => {
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), role: "bot", text, time: formatChatTime() },
    ]);
  };

  const handleSend = async (text) => {
    const content = text ?? input;
    if (!content.trim() || isSending) return;

    appendUserMessage(content);
    setInput("");
    setIsSending(true);
    try {
      const { session_id, reply } = await sendMessage(content, sessionId);
      setSessionId(session_id);
      appendBotMessage(reply);
    } catch (error) {
      // 로그인 만료(401) 등으로 요청이 실패해도 채팅창이 멈추지 않도록 처리
      const status = error?.response?.status;
      if (status === 401) {
        appendBotMessage("로그인이 만료됐어요. 다시 로그인한 뒤 시도해주세요.");
      } else {
        appendBotMessage("답변을 가져오지 못했어요. 잠시 후 다시 시도해주세요.");
      }
      console.error("[AiChatMain] sendMessage failed:", error);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="container chat-page">
      <Link to="/ai-chat" className="chat-page__back">
        ← AI 창업 컨설턴트로 돌아가기
      </Link>
      <h1 className="chat-page__title">AI 창업 컨설턴트</h1>
      <p className="chat-page__desc">회원님의 관심 업종 데이터를 기반으로 맞춤형 상담을 제공합니다.</p>

      <div className="chat-layout">
        <div className="chat-sidebar">
          <Card className="chat-profile">
            <h3>나의 정보</h3>

            <p className="chat-profile__label">관심 업종</p>
            <div className="chat-profile__tags">
              {interests.categories.map((name) => (
                <Tag key={name}>{name}</Tag>
              ))}
            </div>

            <p className="chat-profile__label">관심 지역</p>
            <div className="chat-profile__tags">
              {interests.regions.map((name) => (
                <Tag key={name}>{name}</Tag>
              ))}
            </div>

            <Button variant="outline" className="chat-profile__edit" onClick={goToInfoEdit}>
              정보 수정하기 ↗
            </Button>
          </Card>

          <Card className="chat-history">
            <h3>채팅 내역</h3>
            {chatHistory.length === 0 ? (
              <p className="chat-history__empty">저장된 대화 이력이 없습니다.</p>
            ) : (
              <ul className="chat-history__list">
                {chatHistory.map((entry) => (
                  <li key={entry.id}>
                    <button
                      type="button"
                      className="chat-history__item"
                      onClick={() => restoreConversation(entry)}
                    >
                      <span className="chat-history__item-title">{entry.title}</span>
                      <span className="chat-history__item-time">{entry.savedAt}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>

        <Card className="chat-window">
          <div className="chat-window__messages">
            {messages.map((message) => (
              <ChatBubble key={message.id} {...message} />
            ))}
            {isSending && (
              <ChatBubble role="bot" text="AI가 답변을 작성하고 있어요..." />
            )}
          </div>

          <div className="chat-window__quick-replies">
            {mockQuickReplies.map((question) => (
              <button
                key={question}
                type="button"
                className="chat-window__quick-reply"
                onClick={() => handleSend(question)}
              >
                {question}
              </button>
            ))}
          </div>

          <form
            className="chat-window__input-row"
            onSubmit={(event) => {
              event.preventDefault();
              handleSend();
            }}
          >
            <input
              type="text"
              placeholder="궁금한 내용을 입력하세요..."
              value={input}
              onChange={(event) => setInput(event.target.value)}
            />
            <Button type="submit" className="chat-window__send" disabled={isSending}>
              ⌕
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}

export default AiChatMain;
