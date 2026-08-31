import { useEffect, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faLocationDot,
  faStore,
  faUtensils,
  faMagnifyingGlass,
  faChartLine,
  faLightbulb,
} from "@fortawesome/free-solid-svg-icons";
import {
  getRegions,
  getCategoryGroups,
  getRecommendation,
} from "../api/recommendationApi.js";
import Select from "../components/common/Select.jsx";
import MultiSelectDropdown from "../components/common/MultiSelectDropdown.jsx";
import Button from "../components/common/Button.jsx";
import Card from "../components/common/Card.jsx";
import Badge from "../components/common/Badge.jsx";
import "../styles/AiRecommendation.css";

const BADGE_VARIANT = {
  성장: "good",
  참고: "info",
  공급과잉: "warn",
  쇠퇴: "bad",
};

function ResultPanel({ variant, icon, title, items }) {
  return (
    <Card className={`result-panel result-panel--${variant}`}>
      <div className="result-panel__head">
        <span className="result-panel__head-icon">{icon}</span>
        <span className="result-panel__head-title">{title}</span>
      </div>

      <div className="result-panel__items">
        {items.map((item) => (
          <div className="result-panel__item" key={item.name}>
            <div className="result-panel__item-text">
              <h3>{item.name}</h3>
              <p>{item.description}</p>
            </div>
            <Badge variant={BADGE_VARIANT[item.badge] ?? "info"}>{item.badge}</Badge>
          </div>
        ))}
      </div>
    </Card>
  );
}

function AiRecommendation() {
  const [regions, setRegions] = useState([]);
  const [categoryGroups, setCategoryGroups] = useState([]);
  const [region, setRegion] = useState("");
  const [selectedMajors, setSelectedMajors] = useState([]);
  const [selectedSubs, setSelectedSubs] = useState([]);
  const [result, setResult] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    getRegions().then(setRegions);
    getCategoryGroups().then(setCategoryGroups);
  }, []);

  const subOptions = categoryGroups
    .filter((group) => selectedMajors.includes(group.code))
    .flatMap((group) => group.children);

  const toggleMajor = (code) => {
    setSelectedMajors((prev) =>
      prev.includes(code) ? prev.filter((item) => item !== code) : [...prev, code]
    );
    setSelectedSubs((prev) => {
      const nextMajors = selectedMajors.includes(code)
        ? selectedMajors.filter((item) => item !== code)
        : [...selectedMajors, code];
      const validCodes = new Set(
        categoryGroups
          .filter((group) => nextMajors.includes(group.code))
          .flatMap((group) => group.children.map((child) => child.code))
      );
      return prev.filter((item) => validCodes.has(item));
    });
  };

  const toggleSub = (code) => {
    setSelectedSubs((prev) =>
      prev.includes(code) ? prev.filter((item) => item !== code) : [...prev, code]
    );
  };

  const handleSearch = async () => {
    setIsSearching(true);
    try {
      const data = await getRecommendation({
        region,
        majorCategories: selectedMajors,
        subCategories: selectedSubs,
      });
      setResult(data);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="container ai-recommendation">
      <h1>AI가 추천하는 창업 업종</h1>
      <p className="ai-recommendation__desc">
        지역과 업종을 선택하면 AI가 맞춤형 창업 업종을 분석합니다.
      </p>

      <Card className="ai-recommendation__filter">
        <Select
          label="지역 선택"
          id="region"
          icon={<FontAwesomeIcon icon={faLocationDot} />}
          placeholder="지역을 선택해주세요"
          options={regions}
          value={region}
          onChange={(e) => setRegion(e.target.value)}
        />

        <MultiSelectDropdown
          label="업종 카테고리 (복수 선택)"
          icon={<FontAwesomeIcon icon={faStore} />}
          placeholder="업종 카테고리를 선택해주세요"
          options={categoryGroups}
          selected={selectedMajors}
          onToggle={toggleMajor}
        />

        <MultiSelectDropdown
          label="하위 카테고리 (복수 선택)"
          icon={<FontAwesomeIcon icon={faUtensils} />}
          placeholder="하위 카테고리를 선택해주세요"
          options={subOptions}
          selected={selectedSubs}
          onToggle={toggleSub}
        />

        <Button onClick={handleSearch} disabled={isSearching} className="ai-recommendation__search">
          <FontAwesomeIcon icon={faMagnifyingGlass} /> {isSearching ? "검색 중..." : "검색하기"}
        </Button>
      </Card>

      <section className="ai-recommendation__result">
        <h2>AI 예측 및 추천 결과</h2>
        <p className="ai-recommendation__desc">
          선택한 지역과 업종 데이터를 기반으로 분석한 결과입니다.
        </p>

        {!result && (
          <Card className="ai-recommendation__placeholder">
            지역과 업종을 선택하고 검색하기를 눌러주세요.
          </Card>
        )}

        {result && (
          <>
            <div className="ai-recommendation__grid">
              <ResultPanel
                variant="good"
                icon={<FontAwesomeIcon icon={faChartLine} />}
                title="추천 업종"
                items={[result.recommended]}
              />
              <ResultPanel
                variant="bad"
                icon={<FontAwesomeIcon icon={faChartLine} />}
                title="비추천 업종"
                items={result.notRecommended}
              />
            </div>

            <ResultPanel
              variant="info"
              icon={<FontAwesomeIcon icon={faLightbulb} />}
              title="선택 안 했지만 참고할 업종"
              items={result.reference}
            />
          </>
        )}
      </section>
    </div>
  );
}

export default AiRecommendation;
