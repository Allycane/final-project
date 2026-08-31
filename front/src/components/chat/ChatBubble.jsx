function ChatBubble({ role, text, time }) {
  return (
    <div className={`chat-bubble chat-bubble--${role}`}>
      <div className="chat-bubble__content">
        {text.split("\n").map((line, index) => (
          <p key={index}>{line}</p>
        ))}
      </div>
      {time && <span className="chat-bubble__time">{time}</span>}
    </div>
  );
}

export default ChatBubble;
