import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope } from "@fortawesome/free-regular-svg-icons";
import { faUser, faPhone, faLock } from "@fortawesome/free-solid-svg-icons";
import { signupBasic } from "../api/authApi.js";
import { SIGNUP_STEPS } from "../constants/signup.js";
import StepIndicator from "../components/common/StepIndicator.jsx";
import TextField from "../components/common/TextField.jsx";
import Button from "../components/common/Button.jsx";
import Card from "../components/common/Card.jsx";
import "../styles/Signup.css";
import "../styles/Auth.css";

function SignupBasic() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    passwordConfirm: "",
    phone: "",
  });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    // 전화번호는 하이픈(-) 없이 숫자만 입력받는다. 하이픈은 백엔드에서 붙여준다.
    const nextValue = name === "phone" ? value.replace(/[^0-9]/g, "") : value;
    setForm((prev) => ({ ...prev, [name]: nextValue }));
  };

  const passwordTooShort = form.password.length > 0 && form.password.length < 8;
  const passwordConfirmTooShort =
    form.passwordConfirm.length > 0 && form.passwordConfirm.length < 8;
  const PASSWORD_LENGTH_ERROR = "비밀번호는 8자리 이상이어야 합니다.";

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (form.password.length < 8 || form.passwordConfirm.length < 8) {
      setError(PASSWORD_LENGTH_ERROR);
      return;
    }

    if (form.password !== form.passwordConfirm) {
      setError("비밀번호가 일치하지 않습니다.");
      return;
    }

    setError("");
    setIsSubmitting(true);
    try {
      const basicInfo = await signupBasic(form);
      navigate("/signup/interest", { state: basicInfo });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container signup-page">
      <h1 className="signup-page__title">회원가입</h1>
      <StepIndicator steps={SIGNUP_STEPS} currentStep={1} />

      <Card className="auth-card">
        <form onSubmit={handleSubmit} className="auth-card__columns">
          <div className="auth-card__left">
            <h2>회원가입</h2>
            <p className="auth-card__desc">
              창업 인사이트의 다양한 서비스를
              <br />
              이용해보세요.
            </p>
            <div className="auth-card__illustration" aria-hidden="true">
              <img src="/img/signup/signup_page_1_img.png" alt="" />
            </div>
          </div>

          <div className="auth-card__right">
            <div className="auth-card__row-2col">
              <TextField
                label="이름"
                id="name"
                name="name"
                icon={<FontAwesomeIcon icon={faUser} />}
                placeholder="이름을 입력해주세요"
                value={form.name}
                onChange={handleChange}
                required
              />
              <TextField
                label="전화번호"
                id="phone"
                name="phone"
                type="tel"
                inputMode="numeric"
                maxLength={11}
                icon={<FontAwesomeIcon icon={faPhone} />}
                placeholder="01012345678"
                value={form.phone}
                onChange={handleChange}
                required
              />
            </div>

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
              error={passwordTooShort ? PASSWORD_LENGTH_ERROR : ""}
              required
            />
            <TextField
              label="비밀번호 확인"
              id="passwordConfirm"
              name="passwordConfirm"
              type="password"
              icon={<FontAwesomeIcon icon={faLock} />}
              placeholder="비밀번호를 다시 입력해주세요"
              value={form.passwordConfirm}
              onChange={handleChange}
              error={passwordConfirmTooShort ? PASSWORD_LENGTH_ERROR : ""}
              required
            />

            {error && <p className="signup-page__error">{error}</p>}

            <div className="signup-page__submit-row">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "처리 중..." : "다음 단계로 →"}
              </Button>
            </div>
          </div>
        </form>

        <p className="auth-card__footer">
          이미 계정이 있으신가요? <Link to="/login">로그인</Link>
        </p>
      </Card>
    </div>
  );
}

export default SignupBasic;
