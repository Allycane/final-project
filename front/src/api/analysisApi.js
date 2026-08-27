import { mockAnalysisResult } from "../mocks/analysisResult";

export async function getSalesAnalysis(conditions) {
  // TODO: FastAPI 연동 - axiosInstance의 api를 import해서 실제 엔드포인트로 교체
  // (vite.config.js에 이미 "/predict" → backend:8000 프록시 설정이 되어 있음)
  // import api from "./axiosInstance";
  // const { data } = await api.post("/predict", conditions);
  // return data;
  console.debug("[mock] getSalesAnalysis conditions:", conditions);

  return new Promise((resolve) =>
    setTimeout(() => resolve(mockAnalysisResult), 400)
  );
}
