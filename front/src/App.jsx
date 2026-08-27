import { Routes, Route } from "react-router-dom";
import MainLayout from "./layouts/MainLayout.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import SignupBasic from "./pages/SignupBasic.jsx";
import SignupInterested from "./pages/SignupInterested.jsx";
import AiRecommendation from "./pages/AiRecommendation.jsx";
import AiAnalysis from "./pages/AiAnalysis.jsx";
import AiChatInfo from "./pages/AiChatInfo.jsx";
import AiChatMain from "./pages/AiChatMain.jsx";

function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignupBasic />} />
        <Route path="/signup/interest" element={<SignupInterested />} />
        <Route path="/ai-recommendation" element={<AiRecommendation />} />
        <Route path="/ai-analysis" element={<AiAnalysis />} />
        <Route path="/ai-chat" element={<AiChatInfo />} />
        <Route path="/ai-chat/main" element={<AiChatMain />} />
      </Route>
    </Routes>
  );
}

export default App;
