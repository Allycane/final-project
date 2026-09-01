import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faFaceSmile,
  faChartSimple,
  faArrowTrendUp,
  faShop,
  faMagnifyingGlassLocation,
  faAnglesUp,
  faCircleHalfStroke,
  faLightbulb,
  faClipboardList,
} from "@fortawesome/free-solid-svg-icons";
import { useAuth } from "../hooks/useAuth.js";
import { mockUser } from "../mocks/users.js";
import Button from "../components/common/Button.jsx";
import Card from "../components/common/Card.jsx";
import Tag from "../components/common/Tag.jsx";
import "../styles/AiChatInfo.css";

const ANALYSIS_BASIS = [
  {
    icon: faShop,
    title: "관심 업종 데이터",
    description: "선택하신 관심 업종의 시장 규모, 상권, 경쟁 현황 등 다양한 데이터를 분석합니다.",
  },
  {
    icon: faMagnifyingGlassLocation,
    title: "관심 지역 데이터",
    description: "선택하신 지역의 상권 특성, 유동 인구, 매출 등 지역 기반 데이터로 분석합니다.",
  },
  {
    icon: faAnglesUp,
    title: "창업 환경 분석",
    description: "최신 시장 트렌드와 소비자 패턴을 반영하여 창업 환경을 종합적으로 분석합니다.",
  },
];

const CONSULTING_FEATURES = [
  {
    icon: faCircleHalfStroke,
    title: "시장성 분석",
    description: "선택한 업종과 지역의 시장 규모, 성장 가능성, 경쟁 정도 등을 분석하여 시장성 진입 전략을 제안합니다.",
  },
  {
    icon: faLightbulb,
    title: "창업 아이디어 제안",
    description: "데이터 기반의 창의적인 아이디어와 차별화 포인트를 제안하여 성공 가능성을 높여드립니다.",
  },
  {
    icon: faClipboardList,
    title: "실행 전략 가이드",
    description: "입지 선정, 마케팅 전략, 운영 계획 등 창업 실행에 필요한 구체적인 전략과 가이드를 제공합니다.",
  },
];

function AiChatInfo() {
  const navigate = useNavigate();
  const { user, isLoggedIn } = useAuth();
  const interests = user?.interests ?? mockUser.interests;

  const goToInterestEdit = () => navigate(isLoggedIn ? "/mypage" : "/login");

  return (
    <div className="chat-info">
      <section className="chat-info__hero">
        <div className="container chat-info__hero-inner">
          <div>
            <h1>AI 창업 컨설턴트</h1>
            <p>
              회원님의 관심 업종 데이터를 기반으로 AI가 맞춤형
              <br />
              창업 컨설팅을 제공합니다.
            </p>
          </div>
          <div className="chat-info__hero-icons" aria-hidden="true">
            <span className="chat-info__hero-bubble">
              <FontAwesomeIcon icon={faFaceSmile} />
            </span>
            <span className="chat-info__hero-icon">
              <FontAwesomeIcon icon={faChartSimple} />
            </span>
            <span className="chat-info__hero-icon">
              <FontAwesomeIcon icon={faArrowTrendUp} />
            </span>
          </div>
        </div>
      </section>

      <div className="container chat-info__body">
        <Card className="chat-info__interests">
          <h2>관심 업종 및 창업 정보</h2>
          <p className="chat-info__desc">회원가입 시 입력하신 정보를 기반으로 맞춤형 컨설팅을 제공합니다.</p>

          <div className="chat-info__interests-grid">
            <div>
              <p className="chat-info__interests-label">관심 업종</p>
              <div className="chat-info__tags">
                {interests.categories.map((name) => (
                  <Tag key={name}>{name}</Tag>
                ))}
              </div>
              <button type="button" className="chat-info__edit-link" onClick={goToInterestEdit}>
                관심 업종 수정하기
              </button>
            </div>

            <div>
              <p className="chat-info__interests-label">관심 지역</p>
              <div className="chat-info__tags">
                {interests.regions.map((name) => (
                  <Tag key={name}>{name}</Tag>
                ))}
              </div>
              <button type="button" className="chat-info__edit-link" onClick={goToInterestEdit}>
                관심 지역 수정하기
              </button>
            </div>
          </div>
        </Card>

        <section className="chat-info__section">
          <h2>맞춤형 컨설팅 분석 기준</h2>
          <p className="chat-info__desc">아래 정보를 기반으로 AI가 심층 분석하여 맞춤형 컨설팅을 제공합니다.</p>

          <div className="chat-info__card-grid">
            {ANALYSIS_BASIS.map((item) => (
              <Card className="chat-info__feature-card" key={item.title}>
                <span className="chat-info__feature-icon">
                  <FontAwesomeIcon icon={item.icon} />
                </span>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </Card>
            ))}
          </div>
        </section>

        <section className="chat-info__section">
          <h2>맞춤형 AI 창업 컨설턴트</h2>
          <p className="chat-info__desc">AI가 분석한 데이터를 바탕으로 창업 성공을 위한 인사이트를 제공합니다.</p>

          <div className="chat-info__card-grid">
            {CONSULTING_FEATURES.map((item) => (
              <Card className="chat-info__feature-card" key={item.title}>
                <span className="chat-info__feature-icon">
                  <FontAwesomeIcon icon={item.icon} />
                </span>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </Card>
            ))}
          </div>
        </section>

        <Button block onClick={() => navigate("/ai-chat/main")}>
          AI 컨설턴트와 대화하기
        </Button>

        <Card className="chat-info__notice">
          <h3>✔ 유의사항</h3>
          <ul>
            <li>AI가 제공하는 정보는 데이터 기반의 분석 결과로, 실제 창업 결과를 보장하지 않습니다.</li>
            <li>최종 의사결정은 반드시 본인의 판단과 전문가의 상담 등을 거쳐 신중하게 결정해 주세요.</li>
            <li>개인정보 및 관심 데이터는 안전하게 보호되며, 컨설팅 목적 외에는 사용되지 않습니다.</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}

export default AiChatInfo;
