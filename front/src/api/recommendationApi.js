import { mockRegions } from "../mocks/regions";
import { mockCategoryGroups } from "../mocks/categories";
import { mockRecommendationResult } from "../mocks/recommendationResult";

export async function getRegions() {
  // TODO: FastAPI 연동 - GET /api/regions 로 교체
  return new Promise((resolve) => setTimeout(() => resolve(mockRegions), 100));
}

export async function getCategoryGroups() {
  // TODO: FastAPI 연동 - GET /api/categories 로 교체
  return new Promise((resolve) => setTimeout(() => resolve(mockCategoryGroups), 100));
}

export async function getRecommendation(filters) {
  // TODO: FastAPI 연동 - axiosInstance의 api를 import해서 실제 엔드포인트로 교체
  // import api from "./axiosInstance";
  // const { data } = await api.post("/api/recommendation", filters);
  // return data;
  console.debug("[mock] getRecommendation filters:", filters);

  return new Promise((resolve) =>
    setTimeout(() => resolve(mockRecommendationResult), 300)
  );
}
