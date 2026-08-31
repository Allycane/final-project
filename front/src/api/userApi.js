import { mockUser } from "../mocks/users.js";

export async function getMyProfile() {
  // TODO: FastAPI 연동 - 아래와 같이 axiosInstance를 사용해 실제 엔드포인트로 교체
  // import api from "./axiosInstance";
  // const { data } = await api.get("/api/users/me");
  // return data;

  return new Promise((resolve) => setTimeout(() => resolve(mockUser), 200));
}

export async function updateMyProfile(payload) {
  // TODO: FastAPI 연동 - 기본정보(이름/전화번호/이메일/비밀번호) + 관심정보(업종/지역/매장 형태) 저장 API 연결
  // import api from "./axiosInstance";
  // const { data } = await api.put("/api/users/me", payload);
  // return data;
  console.debug("[mock] updateMyProfile payload:", payload);

  return new Promise((resolve) =>
    setTimeout(() => resolve({ ...mockUser, ...payload }), 300)
  );
}
