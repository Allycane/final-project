import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { loginWithKakao } from "../api/authApi.js";
import { useAuth } from "../hooks/useAuth.js";

function KakaoCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState("");
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    const code = searchParams.get("code");
    if (!code) {
      setError("카카오 로그인 정보를 확인할 수 없습니다.");
      return;
    }

    loginWithKakao(code)
      .then(({ isNewUser, user, kakaoProfile }) => {
        if (isNewUser) {
          alert("회원정보가 존재하지 않아 회원가입을 진행합니다.");
          navigate("/signup/interest", {
            state: { kakaoProfile, isKakaoFlow: true },
            replace: true,
          });
          return;
        }
        login(user);
        navigate("/", { replace: true });
      })
      .catch(() => {
        setError("카카오 로그인 중 오류가 발생했습니다. 다시 시도해주세요.");
      });
  }, [searchParams, navigate, login]);

  return (
    <div className="container auth-page">
      <p>{error || "카카오 로그인 처리 중입니다..."}</p>
    </div>
  );
}

export default KakaoCallback;
