import api from "./axiosInstance";

// 카카오 로그인 페이지로 이동할 때 사용할 인가 요청 URL
export function getKakaoAuthorizeUrl() {
	const params = new URLSearchParams({
		client_id: import.meta.env.VITE_KAKAO_REST_API_KEY ?? "",
		redirect_uri: import.meta.env.VITE_KAKAO_REDIRECT_URI ?? "",
		response_type: "code",
	});
	return `https://kauth.kakao.com/oauth/authorize?${params.toString()}`;
}

export async function login(email, password) {
	const { data } = await api.post("/api/auth/login", { email, password });
	localStorage.setItem("token", data.access_token);
	return data.user;
}

export async function signupBasic(basicInfo) {
	const { data } = await api.post("/api/auth/signup/basic", basicInfo);
	return data;
}

export async function signupInterests(interestInfo) {
	const { data } = await api.post("/api/auth/signup/interests", interestInfo);
	localStorage.setItem("token", data.access_token);
	return data.user;
}

// 새로고침 시 로그인 상태 복원용 함수
export async function getMe() {
	const { data } = await api.get("/api/auth/me");
	return data;
}

// 카카오 로그인: 인가 코드를 백엔드로 전달해 로그인/신규가입 여부를 확인한다.
// 기존 회원이면 { isNewUser: false, user }, 신규 회원이면 { isNewUser: true, kakaoProfile } 형태로 응답한다.
export async function loginWithKakao(code) {
	const { data } = await api.post("/api/auth/kakao", { code });
	if (!data.is_new_user) {
		localStorage.setItem("token", data.access_token);
	}
	return {
		isNewUser: data.is_new_user,
		user: data.user,
		kakaoProfile: data.kakao_profile,
	};
}

// 카카오 신규 회원의 관심 정보 선택 후 최종 가입 처리
export async function kakaoSignupInterests(payload) {
	const { data } = await api.post("/api/auth/kakao/signup/interests", payload);
	localStorage.setItem("token", data.access_token);
	return data.user;
}

// import { mockUser } from "../mocks/users";

// export async function login(email, password) {
//   // TODO: FastAPI 연동 - 아래와 같이 axiosInstance를 사용해 실제 엔드포인트로 교체
//   // import api from "./axiosInstance";
//   // const { data } = await api.post("/api/auth/login", { email, password });
//   // return data;

//   return new Promise((resolve, reject) => {
//     setTimeout(() => {
//       if (email && password) {
//         resolve({ ...mockUser, email });
//       } else {
//         reject(new Error("이메일과 비밀번호를 입력해주세요."));
//       }
//     }, 300);
//   });
// }

// export async function signupBasic(basicInfo) {
//   // TODO: FastAPI 연동 - 회원가입 1단계(기본정보) 저장 API 연결
//   // const { data } = await api.post("/api/auth/signup/basic", basicInfo);
//   // return data;

//   return new Promise((resolve) => setTimeout(() => resolve({ ...basicInfo }), 300));
// }

// export async function signupInterests(interestInfo) {
//   // TODO: FastAPI 연동 - 회원가입 2단계(관심정보) 저장 및 가입 완료 처리 API 연결
//   // const { data } = await api.post("/api/auth/signup/interests", interestInfo);
//   // return data;
//   // (위 두 함수 모두 연동 시 "./axiosInstance"의 api 인스턴스를 import해서 사용)

//   return new Promise((resolve) =>
//     setTimeout(() => resolve({ ...mockUser, interests: interestInfo }), 300)
//   );
// }
