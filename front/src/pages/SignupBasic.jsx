import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope, faEye, faEyeSlash } from "@fortawesome/free-regular-svg-icons";
import { faUser, faPhone, faLock } from "@fortawesome/free-solid-svg-icons";
import { signupBasic } from "../api/authApi.js";
import { SIGNUP_STEPS } from "../constants/signup.js";
import { formatPhoneNumber, toPhoneDigits } from "../utils/phone.js";
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
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    // 프론트에서는 010-1234-5678 형식으로 입력받고, 백엔드 전송 시 숫자만 남긴다.
    const nextValue = name === "phone" ? formatPhoneNumber(value) : value;
    setForm((prev) => ({ ...prev, [name]: nextValue }));
  };

  const PASSWORD_LENGTH_ERROR = "비밀번호는 8자리 이상이어야 합니다.";
  const PASSWORD_MISMATCH_ERROR = "비밀번호가 일치하지 않습니다.";

  const passwordTooShort = form.password.length > 0 && form.password.length < 8;
  const passwordConfirmTooShort =
    form.passwordConfirm.length > 0 && form.passwordConfirm.length < 8;
  const passwordMismatch =
    !passwordConfirmTooShort &&
    form.passwordConfirm.length > 0 &&
    form.password !== form.passwordConfirm;

  const passwordConfirmError = passwordConfirmTooShort
    ? PASSWORD_LENGTH_ERROR
    : passwordMismatch
      ? PASSWORD_MISMATCH_ERROR
      : "";

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (form.password.length < 8 || form.passwordConfirm.length < 8) return;
    if (form.password !== form.passwordConfirm) return;

    setIsSubmitting(true);
    try {
      const basicInfo = await signupBasic({
        ...form,
        phone: toPhoneDigits(form.phone),
      });
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
                maxLength={13}
                icon={<FontAwesomeIcon icon={faPhone} />}
                placeholder="010-1234-5678"
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
              type={showPassword ? "text" : "password"}
              icon={<FontAwesomeIcon icon={faLock} />}
              rightIcon={
                <FontAwesomeIcon
                  icon={showPassword ? faEyeSlash : faEye}
                  onClick={() => setShowPassword((prev) => !prev)}
                />
              }
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
              type={showPasswordConfirm ? "text" : "password"}
              icon={<FontAwesomeIcon icon={faLock} />}
              rightIcon={
                <FontAwesomeIcon
                  icon={showPasswordConfirm ? faEyeSlash : faEye}
                  onClick={() => setShowPasswordConfirm((prev) => !prev)}
                />
              }
              placeholder="비밀번호를 다시 입력해주세요"
              value={form.passwordConfirm}
              onChange={handleChange}
              error={passwordConfirmError}
              required
            />

            <div className="signup-page__submit-row">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "처리 중..." : "다음 단계로 →"}
              </Button>
            </div>
          </div>
        </form>

        <p className="auth-card__footer">
          이미 계정이 있으신가요?{" "}
          <Link to="/login" state={{ from: "/signup" }}>
            로그인
          </Link>
        </p>
      </Card>
    </div>
  );
}

export default SignupBasic;
