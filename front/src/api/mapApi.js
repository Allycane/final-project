import api from "./axiosInstance";

export async function getDistribution(filters) {
	const { data } = await api.post("/api/analysis/map", filters);
	return data;
}
