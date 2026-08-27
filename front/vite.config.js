// 가장 기본 설정이었던 vite.config.js 코드 내용
// import react from '@vitejs/plugin-react'
// import { defineConfig } from 'vite'

// // https://vite.dev/config/
// export default defineConfig({
//   plugins: [react()],
// })

//docker
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
	plugins: [react()],

	server: {
		host: "0.0.0.0",
		port: 5173,

		proxy: {
			"/predict": {
				target: "http://backend:8000",
				changeOrigin: true,
			},
		},
	},
});
