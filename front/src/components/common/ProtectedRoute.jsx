import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth.js";

function ProtectedRoute() {
	const { isLoggedIn, isLoading } = useAuth();

	if (isLoading) {
		return <div className="container">로딩 중...</div>;
	}

	if (!isLoggedIn) {
		return <Navigate to="/" replace />;
	}

	return <Outlet />;
}

export default ProtectedRoute;
