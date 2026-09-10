// ===== 수정 시작 (recent-selections 연동, 신규/전면 수정 파일) =====
import api from "./axiosInstance";

export async function fetchRecentSelections(featureKey) {
	const { data } = await api.get("/api/recent-selections", {
		params: { feature_key: featureKey },
	});
	return data; // [{ id, label, payload }, ...]
}

export async function saveRecentSelection(featureKey, entry) {
	const { label, ...payload } = entry;
	const { data } = await api.post("/api/recent-selections", {
		feature_key: featureKey,
		label,
		payload,
	});
	return data;
}

export async function deleteRecentSelection(id) {
	await api.delete(`/api/recent-selections/${id}`);
}
// ===== 수정 끝 =====
