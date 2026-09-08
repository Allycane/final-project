import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth.js";

function ProtectedRoute() {
	const { isLoggedIn, isLoading } = useAuth();
	const location = useLocation();

	if (isLoading) {
		return <div className="container">로딩 중...</div>;
	}

	if (!isLoggedIn) {
		const from = `${location.pathname}${location.search}`;
		return (
			<Navigate to="/login" replace state={{ authRequired: true, from }} />
		);
	}

	return <Outlet />;
}

export default ProtectedRoute;
