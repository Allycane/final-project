import { useEffect, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faLocationDot,
  faStore,
  faMagnifyingGlass,
  faChartLine,
  faLightbulb,
} from "@fortawesome/free-solid-svg-icons";
import {
  getRegions,
  getCategoryGroups,
  getRecommendation,
} from "../api/recommendationApi.js";
import { useRecentSelections } from "../hooks/useRecentSelections.js";
import MultiSelectDropdown from "../components/common/MultiSelectDropdown.jsx";
import RecentSelections from "../components/common/RecentSelections.jsx";
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

const MIN_SUB_CATEGORIES = 3;

function ResultPanel({ variant, icon, title, items, disabled, disabledMessage }) {
  return (
    <Card
      className={`result-panel result-panel--${variant} ${
        disabled ? "result-panel--disabled" : ""
      }`.trim()}
    >
      <div className="result-panel__head">
        <span className="result-panel__head-icon">{icon}</span>
        <span className="result-panel__head-title">{title}</span>
      </div>

      {disabled ? (
        <p className="result-panel__disabled-message">{disabledMessage}</p>
      ) : (
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
      )}
    </Card>
  );
}

function AiRecommendation() {
  const [regions, setRegions] = useState([]);
  const [categoryGroups, setCategoryGroups] = useState([]);
  const [region, setRegion] = useState("");
  const [selectedMajor, setSelectedMajor] = useState("");
  const [selectedSubs, setSelectedSubs] = useState([]);
  const [result, setResult] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const { items: recentItems, addSelection, removeSelection } =
    useRecentSelections("recentSelections:ai-recommendation");

  useEffect(() => {
    getRegions().then(setRegions);
    getCategoryGroups().then(setCategoryGroups);
  }, []);

  const subOptions =
    categoryGroups.find((group) => group.code === selectedMajor)?.children ?? [];
  const allSubsSelected =
    subOptions.length > 0 && selectedSubs.length === subOptions.length;
  const hasEnoughSubs = selectedSubs.length >= MIN_SUB_CATEGORIES;

  const allSubOptions = categoryGroups.flatMap((group) => group.children);
  const regionName = (code) => regions.find((r) => r.code === code)?.name ?? code;
  const majorName = (code) =>
    categoryGroups.find((group) => group.code === code)?.name ?? code;
  const subNames = (codes) =>
    codes.map((code) => allSubOptions.find((c) => c.code === code)?.name ?? code).join(", ");

  const chooseMajor = (code) => {
    setSelectedMajor(code);
    setSelectedSubs([]);
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
        majorCategory: selectedMajor,
        subCategories: selectedSubs,
      });
      setResult(data);
      addSelection({
        label: `${regionName(region)} · ${majorName(selectedMajor)} · ${subNames(
          selectedSubs,
        )}`,
        region,
        major: selectedMajor,
        subs: selectedSubs,
      });
    } finally {
      setIsSearching(false);
    }
  };

  const restoreSelection = (item) => {
    setRegion(item.region);
    setSelectedMajor(item.major);
    setSelectedSubs(item.subs);
  };

  return (
    <div className="container ai-recommendation">
      <h1>AI가 추천하는 창업 업종</h1>
      <p className="ai-recommendation__desc">
        지역과 업종을 선택하면 AI가 맞춤형 창업 업종을 분석합니다.
      </p>

      <RecentSelections
        items={recentItems}
        onSelect={restoreSelection}
        onRemove={removeSelection}
      />

      <Card className="ai-recommendation__filter">
        <MultiSelectDropdown
          label="지역 선택"
          icon={<FontAwesomeIcon icon={faLocationDot} />}
          placeholder="지역을 선택해주세요"
          options={regions}
          selected={region ? [region] : []}
          onToggle={setRegion}
          single
        />

        <MultiSelectDropdown
          label="업종 카테고리 (단일 선택)"
          icon={<FontAwesomeIcon icon={faStore} />}
          placeholder="업종 카테고리를 선택해주세요"
          options={categoryGroups}
          selected={selectedMajor ? [selectedMajor] : []}
          onToggle={chooseMajor}
          single
        />

        <MultiSelectDropdown
          label="하위 카테고리 (복수 선택)"
          placeholder="3개 이상 선택 필수"
          options={subOptions}
          selected={selectedSubs}
          onToggle={toggleSub}
        />

        <Button
          onClick={handleSearch}
          disabled={isSearching || !region || !hasEnoughSubs}
          className="ai-recommendation__search"
        >
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
              title="참고할만 한 업종"
              items={result.reference}
              disabled={allSubsSelected}
              disabledMessage="하위 카테고리를 모두 선택하여 참고할만 한 업종이 없습니다."
            />
          </>
        )}
      </section>
    </div>
  );
}

export default AiRecommendation;
