import { mockUser } from "../mocks/users";

export async function login(email, password) {
  // TODO: FastAPI 연동 - 아래와 같이 axiosInstance를 사용해 실제 엔드포인트로 교체
  // import api from "./axiosInstance";
  // const { data } = await api.post("/api/auth/login", { email, password });
  // return data;

  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (email && password) {
        resolve({ ...mockUser, email });
      } else {
        reject(new Error("이메일과 비밀번호를 입력해주세요."));
      }
    }, 300);
  });
}

export async function signupBasic(basicInfo) {
  // TODO: FastAPI 연동 - 회원가입 1단계(기본정보) 저장 API 연결
  // const { data } = await api.post("/api/auth/signup/basic", basicInfo);
  // return data;

  return new Promise((resolve) => setTimeout(() => resolve({ ...basicInfo }), 300));
}

export async function signupInterests(interestInfo) {
  // TODO: FastAPI 연동 - 회원가입 2단계(관심정보) 저장 및 가입 완료 처리 API 연결
  // const { data } = await api.post("/api/auth/signup/interests", interestInfo);
  // return data;
  // (위 두 함수 모두 연동 시 "./axiosInstance"의 api 인스턴스를 import해서 사용)

  return new Promise((resolve) =>
    setTimeout(() => resolve({ ...mockUser, interests: interestInfo }), 300)
  );
}
