import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope } from "@fortawesome/free-regular-svg-icons";
import { faLock } from "@fortawesome/free-solid-svg-icons";
import { login as loginRequest } from "../api/authApi.js";
import { useAuth } from "../hooks/useAuth.js";
import TextField from "../components/common/TextField.jsx";
import Checkbox from "../components/common/Checkbox.jsx";
import Button from "../components/common/Button.jsx";
import Card from "../components/common/Card.jsx";
import "../styles/Auth.css";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "", keepLoggedIn: false });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const user = await loginRequest(form.email, form.password);
      login(user);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container auth-page">
      <Card className="auth-card">
        <form onSubmit={handleSubmit} className="auth-card__columns">
          <div className="auth-card__left">
            <h1>로그인</h1>
            <p className="auth-card__desc">
              창업 인사이트의 다양한 서비스를
              <br />
              이용해보세요.
            </p>
            <div className="auth-card__illustration" aria-hidden="true">
              <img src="/img/login/login_img.png" alt="" />
            </div>
          </div>

          <div className="auth-card__right">
            <TextField
              label="이메일"
              id="email"
              name="email"
              type="email"
              icon={<FontAwesomeIcon icon={faEnvelope} />}
              placeholder="이메일을 입력해주세요"
              value={form.email}
              onChange={handleChange}
              required
            />
            <TextField
              label="비밀번호"
              id="password"
              name="password"
              type="password"
              icon={<FontAwesomeIcon icon={faLock} />}
              placeholder="비밀번호를 입력해주세요"
              value={form.password}
              onChange={handleChange}
              required
            />

            <div className="auth-card__row">
              <Checkbox
                id="keepLoggedIn"
                name="keepLoggedIn"
                label="로그인 상태 유지"
                checked={form.keepLoggedIn}
                onChange={handleChange}
              />
              <div className="auth-card__links">
                <Link to="/">아이디 찾기</Link>
                <span>|</span>
                <Link to="/">비밀번호 찾기</Link>
              </div>
            </div>

            {error && <p className="auth-card__error">{error}</p>}

            <Button type="submit" block disabled={isSubmitting}>
              {isSubmitting ? "로그인 중..." : "로그인"}
            </Button>
          </div>
        </form>

        <p className="auth-card__footer">
          아직 계정이 없으신가요? <Link to="/signup">회원가입</Link>
        </p>
      </Card>
    </div>
  );
}

export default Login;
