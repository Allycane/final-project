import api from "./axiosInstance";

export async function getMyProfile() {
	const { data } = await api.get("/api/auth/me");
	return data;
}

//POST -> PATCH로 변경
//   export async function updateMyProfile(payload) {
//     const { data } = await api.post("/api/auth/me/update", payload);
//     return data;
//   }
export async function updateMyProfile(payload) {
	const { data } = await api.patch("/api/auth/me/update", payload);
	return data;
}

export async function deleteMyAccount() {
	const { data } = await api.delete("/api/auth/me");
	return data;
}
