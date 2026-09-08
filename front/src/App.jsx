import { Routes, Route } from "react-router-dom";
import MainLayout from "./layouts/MainLayout.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import SignupBasic from "./pages/SignupBasic.jsx";
import SignupInterested from "./pages/SignupInterested.jsx";
import KakaoCallback from "./pages/KakaoCallback.jsx";
import AiRecommendation from "./pages/AiRecommendation.jsx";
import AiAnalysis from "./pages/AiAnalysis.jsx";
import AiAnalysisComparison from "./pages/AiAnalysisComparison.jsx";
import AiChatInfo from "./pages/AiChatInfo.jsx";
import AiChatMain from "./pages/AiChatMain.jsx";
import Mypage from "./pages/Mypage.jsx";
import ProtectedRoute from "./components/common/ProtectedRoute.jsx";
import ScrollToTop from "./components/common/ScrollToTop.jsx";

function App() {
	return (
		<>
			<ScrollToTop />
			<Routes>
				<Route element={<MainLayout />}>
					<Route path="/" element={<Home />} />
					<Route path="/login" element={<Login />} />
					<Route path="/signup" element={<SignupBasic />} />
					<Route path="/signup/interest" element={<SignupInterested />} />
					<Route path="/oauth/kakao/callback" element={<KakaoCallback />} />
					<Route path="/ai-recommendation" element={<AiRecommendation />} />
					<Route path="/ai-analysis" element={<AiAnalysis />} />
					<Route
						path="/ai-analysis/comparison"
						element={<AiAnalysisComparison />}
					/>
					<Route path="/ai-chat" element={<AiChatInfo />} />
					<Route element={<ProtectedRoute />}>
						<Route path="/mypage" element={<Mypage />} />
						<Route path="/ai-chat/main" element={<AiChatMain />} />
						{/* 로그인이나 가입한 사람이 아니면 접근 못하도록 막음 */}
					</Route>
					{/* <Route path="/ai-chat/main" element={<AiChatMain />} /> */}
					{/* <Route path="/mypage" element={<Mypage />} /> */}
				</Route>
			</Routes>
		</>
	);
}

export default App;
