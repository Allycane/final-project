// 전화번호는 프론트에서 010-1234-5678 형식으로 표시/입력받고,
// 백엔드에는 01012345678(숫자만)로 저장한다.

export function formatPhoneNumber(value) {
  const digits = (value ?? "").replace(/[^0-9]/g, "").slice(0, 11);

  if (digits.length < 4) return digits;
  if (digits.length < 8) return `${digits.slice(0, 3)}-${digits.slice(3)}`;
  return `${digits.slice(0, 3)}-${digits.slice(3, 7)}-${digits.slice(7)}`;
}

export function toPhoneDigits(value) {
  return (value ?? "").replace(/[^0-9]/g, "");
}
