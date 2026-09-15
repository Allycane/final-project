import api from "./axiosInstance";

export async function getRegions() {
	const { data } = await api.get("/api/regions");
	return data;
}

export async function getCategoryGroups() {
	const { data } = await api.get("/api/categories");
	return data;
}

export async function getStoreTypes() {
	const { data } = await api.get("/api/store-types");
	return data;
}

export async function getRecommendation(filters) {
	const { data } = await api.post("/api/recommendation", filters);
	return data;
}
