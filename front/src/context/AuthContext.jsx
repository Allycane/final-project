import { useState, useEffect } from "react";
import { AuthContext } from "./authContext.js";
import { getMe } from "../api/authApi.js";
import { useNavigate } from "react-router-dom";

export function AuthProvider({ children }) {
	const [user, setUser] = useState(null);
	const navigate = useNavigate();

	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		const token = localStorage.getItem("token");
		if (!token) {
			setIsLoading(false);
			return;
		}
		getMe()
			.then((userData) => setUser(userData))
			.catch(() => {
				localStorage.removeItem("token");
				setUser(null);
			})
			.finally(() => setIsLoading(false));
	}, []);

	const login = (userData) => setUser(userData);

	const logout = () => {
		setUser(null);
		localStorage.removeItem("token");
		navigate("/");
	};

	return (
		<AuthContext.Provider
			value={{ user, isLoggedIn: !!user, isLoading, login, logout }}
		>
			{children}
		</AuthContext.Provider>
	);
}

// import { useState } from "react";
// import { AuthContext } from "./authContext.js";

// export function AuthProvider({ children }) {
//   const [user, setUser] = useState(null);

//   const login = (userData) => setUser(userData);
//   const logout = () => setUser(null);

//   return (
//     <AuthContext.Provider value={{ user, isLoggedIn: !!user, login, logout }}>
//       {children}
//     </AuthContext.Provider>
//   );
// }
