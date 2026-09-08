const chatTimeFormatter = new Intl.DateTimeFormat("ko-KR", {
  hour: "numeric",
  minute: "2-digit",
  hour12: true,
});

export function formatChatTime(date = new Date()) {
  return chatTimeFormatter.format(date);
}
