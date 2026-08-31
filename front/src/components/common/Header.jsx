import { useState } from "react";
import { NavLink } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBars, faXmark } from "@fortawesome/free-solid-svg-icons";
import { useAuth } from "../../hooks/useAuth.js";
import "../../styles/Header.css";

const NAV_LINKS = [
  { to: "/", label: "홈" },
  { to: "/ai-recommendation", label: "AI 추천 업종" },
  { to: "/ai-analysis", label: "AI 매출 분석" },
  { to: "/ai-chat", label: "AI 창업 컨설턴트" },
];

function Header() {
  const { user, isLoggedIn, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const closeMenu = () => setIsMenuOpen(false);

  return (
    <header className="header">
      <div className="header__inner container">
        <NavLink to="/" className="header__logo" onClick={closeMenu}>
          <img src="/img/Logo.png" alt="StartOn" height={28} />
        </NavLink>

        <nav className={`header__nav ${isMenuOpen ? "is-open" : ""}`.trim()}>
          {NAV_LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              onClick={closeMenu}
              className={({ isActive }) =>
                `header__nav-link ${isActive ? "is-active" : ""}`.trim()
              }
            >
              {link.label}
            </NavLink>
          ))}

          <div className="header__auth header__auth--mobile">
            {isLoggedIn ? (
              <>
                <span className="header__welcome">반갑습니다, {user.name} 회원님!</span>
                <NavLink to="/mypage" className="btn btn-outline" onClick={closeMenu}>
                  마이페이지
                </NavLink>
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => {
                    logout();
                    closeMenu();
                  }}
                >
                  로그아웃
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className="btn btn-outline" onClick={closeMenu}>
                  로그인
                </NavLink>
                <NavLink to="/signup" className="btn btn-primary" onClick={closeMenu}>
                  회원가입
                </NavLink>
              </>
            )}
          </div>
        </nav>

        <div className="header__auth header__auth--desktop">
          {isLoggedIn ? (
            <>
              <span className="header__welcome">반갑습니다, {user.name} 회원님!</span>
              <NavLink to="/mypage" className="btn btn-outline">
                마이페이지
              </NavLink>
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

        <button
          type="button"
          className="header__menu-toggle"
          aria-label={isMenuOpen ? "메뉴 닫기" : "메뉴 열기"}
          onClick={() => setIsMenuOpen((prev) => !prev)}
        >
          <FontAwesomeIcon icon={isMenuOpen ? faXmark : faBars} />
        </button>
      </div>
    </header>
  );
}

export default Header;
