import axios from "axios";

// TODO: FastAPI 연동 - .env의 VITE_API_BASE_URL을 실제 배포 주소로 교체하면
// 아래 인스턴스를 그대로 각 도메인 api(*.js)에서 사용할 수 있습니다.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
