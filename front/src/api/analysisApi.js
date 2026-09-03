// import { mockAnalysisResult } from "../mocks/analysisResult";

// export async function getSalesAnalysis(conditions) {
//   // TODO: FastAPI 연동 - axiosInstance의 api를 import해서 실제 엔드포인트로 교체
//   // (vite.config.js에 이미 "/predict" → backend:8000 프록시 설정이 되어 있음)
//   // import api from "./axiosInstance";
//   // const { data } = await api.post("/predict", conditions);
//   // return data;
//   console.debug("[mock] getSalesAnalysis conditions:", conditions);

//   return new Promise((resolve) =>
//     setTimeout(() => resolve(mockAnalysisResult), 400)
//   );
// }

import api from "./axiosInstance";

export async function getSalesAnalysis(conditions) {
	// targetSales는 TextField(placeholder "예: 5,000")라 콤마가 섞여 올 수 있어
	// 서버 스키마(int)에 맞게 숫자만 남겨서 보낸다.
	const payload = {
		...conditions,
		targetSales:
			Number(String(conditions.targetSales).replace(/[^0-9]/g, "")) || 0,
	};

	const { data } = await api.post("/api/analysis", payload);
	return data;
}
