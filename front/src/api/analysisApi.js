import api from "./axiosInstance";

export async function getActualCategoryGroups() {
	// AI 매출 분석 전용 - 실측(actual) 데이터가 존재하는 업종만 내려주는 엔드포인트.
	// recommendationApi.getCategoryGroups()(/api/categories)는 Page1 추천용이라 그대로 둔다.
	const { data } = await api.get("/api/analysis/categories");
	return data;
}

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
