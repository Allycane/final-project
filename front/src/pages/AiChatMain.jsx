import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  sendMessage,
  fetchChatHistory,
  fetchSessionMessages,
  deleteChatHistoryEntry,
} from "../api/chatApi.js";
import { mockInitialMessages, mockQuickReplies } from "../mocks/chatMessages.js";
import { useAuth } from "../hooks/useAuth.js";
import { mockUser } from "../mocks/users.js";
import { formatChatTime } from "../utils/time.js";
import ChatBubble from "../components/chat/ChatBubble.jsx";
import Card from "../components/common/Card.jsx";
import Button from "../components/common/Button.jsx";
import Tag from "../components/common/Tag.jsx";
import "../styles/Chat.css";

// 비로그인 게스트용 폴백. 로그인 사용자는 서버(DB)에 저장되므로 이 값을 쓰지 않는다.
const CHAT_HISTORY_KEY = "chatHistory:ai-chat-main";
const MAX_CHAT_HISTORY = 3;

function readChatHistory() {
  try {
    const raw = localStorage.getItem(CHAT_HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeChatHistory(history) {
  localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(history));
}

// 서버가 내려주는 ISO 타임스탬프(created_at)를 채팅 말풍선/내역에 쓰는 표시용 문자열로 변환.
function formatServerTime(isoString) {
  try {
    return new Date(isoString).toLocaleTimeString("ko-KR", {
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return "";
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
  const [chatHistory, setChatHistory] = useState(() => (isLoggedIn ? [] : readChatHistory()));

  // 로그인한 사용자는 마운트 시(=페이지에 들어올 때마다, 새로고침 포함) 서버에 저장된
  // 채팅 내역을 조회해온다. 매 메시지마다 이미 서버에 즉시 저장되므로 새로고침해도 그대로 남아있다.
  useEffect(() => {
    if (!isLoggedIn) return;
    fetchChatHistory()
      .then((summaries) =>
        setChatHistory(
          summaries.map((s) => ({
            id: s.id,
            title: s.title,
            savedAt: formatServerTime(s.created_at),
          })),
        ),
      )
      .catch((error) => console.error("[AiChatMain] fetchChatHistory failed:", error));
  }, [isLoggedIn]);

  const restoreConversation = async (entry) => {
    // 비로그인 게스트의 localStorage 항목은 메시지 전체를 이미 갖고 있다.
    if (entry.messages) {
      setMessages(entry.messages);
      setSessionId(null);
      return;
    }

    // 로그인 사용자는 목록에 메시지가 없으므로(가벼운 요약만 받음) 클릭 시점에 전체를 조회한다.
    try {
      const { messages: serverMessages } = await fetchSessionMessages(entry.id);
      setMessages(
        serverMessages.map((m, index) => ({
          id: `${entry.id}-${index}`,
          role: m.role === "assistant" ? "bot" : "user",
          text: m.content,
          time: formatServerTime(m.created_at),
        })),
      );
      setSessionId(entry.id);
    } catch (error) {
      console.error("[AiChatMain] fetchSessionMessages failed:", error);
    }
  };

  // "채팅 내역" 목록에서 개별 대화를 삭제한다.
  // 채팅창을 초기 인사말 화면으로 되돌린다 (진행 중인 대화 맥락도 함께 초기화).
  const resetToInitialConversation = () => {
    setMessages(mockInitialMessages.map((message) => ({ ...message, time: formatChatTime() })));
    setSessionId(null);
  };

  const handleDeleteHistory = (event, entryId) => {
    event.stopPropagation(); // 항목 버튼(복원)이 같이 클릭되지 않도록 막는다.

    const next = chatHistory.filter((entry) => entry.id !== entryId);
    setChatHistory(next);

    if (isLoggedIn) {
      deleteChatHistoryEntry(entryId).catch((error) =>
        console.error("[AiChatMain] deleteChatHistoryEntry failed:", error),
      );
    } else {
      writeChatHistory(next);
    }

    // 저장된 대화 이력을 전부 지웠다면, 화면에 예전 대화가 계속 떠 있지 않도록
    // 채팅창도 초기 화면으로 되돌린다.
    if (next.length === 0) {
      resetToInitialConversation();
    }
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
      // 로그인 만료(401), 타임아웃 등 상황별로 안내 문구를 구분해서 채팅창이 멈추지 않도록 처리
      const status = error?.response?.status;
      const isTimeout = error?.code === "ECONNABORTED" || /timeout/i.test(error?.message ?? "");

      if (status === 401) {
        appendBotMessage("로그인이 만료됐어요. 다시 로그인한 뒤 시도해주세요.");
      } else if (isTimeout) {
        appendBotMessage("답변 생성이 예상보다 오래 걸리고 있어요. 잠시 후 다시 시도해주세요.");
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
                    <button
                      type="button"
                      className="chat-history__delete"
                      aria-label="대화 내역 삭제"
                      onClick={(event) => handleDeleteHistory(event, entry.id)}
                    >
                      ×
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
