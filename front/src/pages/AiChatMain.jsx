import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { sendMessage } from "../api/chatApi.js";
import { mockInitialMessages, mockQuickReplies } from "../mocks/chatMessages.js";
import { useAuth } from "../hooks/useAuth.js";
import { mockUser } from "../mocks/users.js";
import ChatBubble from "../components/chat/ChatBubble.jsx";
import Card from "../components/common/Card.jsx";
import Button from "../components/common/Button.jsx";
import Tag from "../components/common/Tag.jsx";
import "../styles/Chat.css";

function AiChatMain() {
  const navigate = useNavigate();
  const { user, isLoggedIn } = useAuth();
  const interests = user?.interests ?? mockUser.interests;

  const goToInfoEdit = () => navigate(isLoggedIn ? "/mypage" : "/login");

  const [messages, setMessages] = useState(mockInitialMessages);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const appendUserMessage = (text) => {
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), role: "user", text, time: "지금" },
    ]);
  };

  const handleSend = async (text) => {
    const content = text ?? input;
    if (!content.trim() || isSending) return;

    appendUserMessage(content);
    setInput("");
    setIsSending(true);
    try {
      const reply = await sendMessage(content);
      setMessages((prev) => [...prev, { ...reply, time: "지금" }]);
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
