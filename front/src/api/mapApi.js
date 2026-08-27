import { mockMapPoints, mockMapCenter } from "../mocks/mapPoints";

export async function getDistribution(filters) {
  // TODO: FastAPI 연동 - axiosInstance의 api를 import해서 실제 엔드포인트로 교체
  // import api from "./axiosInstance";
  // const { data } = await api.post("/api/analysis/map", filters);
  // return data;
  console.debug("[mock] getDistribution filters:", filters);

  return new Promise((resolve) =>
    setTimeout(() => resolve({ center: mockMapCenter, points: mockMapPoints }), 300)
  );
}
