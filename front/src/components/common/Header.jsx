import { NavLink } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth.js";
import "./Header.css";

const NAV_LINKS = [
  { to: "/", label: "홈" },
  { to: "/ai-recommendation", label: "AI 추천 업종" },
  { to: "/ai-analysis", label: "AI 매출 분석" },
  { to: "/ai-chat", label: "AI 창업 컨설턴트" },
];

function Header() {
  const { user, isLoggedIn, logout } = useAuth();

  return (
    <header className="header">
      <div className="header__inner container">
        <NavLink to="/" className="header__logo">
          <img src="/img/Logo.png" alt="StartOn" height={28} />
        </NavLink>

        <nav className="header__nav">
          {NAV_LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `header__nav-link ${isActive ? "is-active" : ""}`.trim()
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="header__auth">
          {isLoggedIn ? (
            <>
              <span className="header__welcome">반갑습니다, {user.name} 회원님!</span>
              <button type="button" className="btn btn-outline" onClick={logout}>
                로그아웃
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="btn btn-outline">
                로그인
              </NavLink>
              <NavLink to="/signup" className="btn btn-primary">
                회원가입
              </NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
