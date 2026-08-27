import { useNavigate } from "react-router-dom";
import Button from "../components/common/Button.jsx";
import Card from "../components/common/Card.jsx";
import "./Home.css";

const FEATURES = [
  {
    icon: "📊",
    title: "실제 데이터 기반 분석",
    description: "공공 데이터와 상권 데이터를 AI가 분석합니다.",
  },
  {
    icon: "🎯",
    title: "정확한 업종 추천",
    description: "성공 가능성이 높은 업종을 추천해드립니다.",
  },
  {
    icon: "📍",
    title: "지역 맞춤 분석",
    description: "지역별 상권과 트렌드를 반영합니다.",
  },
  {
    icon: "✅",
    title: "누구나 쉽게 활용",
    description: "복잡한 데이터를 쉽게 이해하고 활용할 수 있습니다.",
  },
];

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home">
      <section className="home__hero">
        <div className="container home__hero-inner">
          <div className="home__hero-text">
            <h1>
              AI가 분석하고,
              <br />
              성공 가능한 창업을
              <br />
              <span className="home__accent">추천해드려요</span>
            </h1>
            <p>
              빅데이터와 AI 분석을 기반으로
              <br />
              나에게 딱 맞는 창업 아이템과 지역을 추천합니다.
            </p>
            <Button onClick={() => navigate("/ai-recommendation")}>
              AI 창업 업종 추천 시작하기 →
            </Button>
          </div>
          <div className="home__hero-image">
            <img src="/img/home/home_hero_img.png" alt="AI 창업 분석 대시보드" />
          </div>
        </div>
      </section>

      <section className="container home__features">
        <h2>왜 창업 인사이트인가요?</h2>
        <div className="home__feature-grid">
          {FEATURES.map((feature) => (
            <Card key={feature.title} className="home__feature-card">
              <div className="home__feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Home;
