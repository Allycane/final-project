import { useEffect, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faLocationDot,
  faStore,
  faMagnifyingGlass,
  faChartLine,
  faLightbulb,
  faCircleExclamation,
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
  "성장 둔화 우려": "bad",
  "예측 데이터": "warn",
};

const MIN_SUB_CATEGORIES = 3;

// 이 대분류를 선택했을 때만 "예측 데이터 부족" 안내 블록을 보여준다
// (CS1=외식업은 실측 데이터가 충분해서 해당 사항이 거의 없음).
const MOCK_NOTICE_MAJOR_CODES = ["CS2", "CS3"];

function ResultPanel({ variant, icon, title, items, disabled, disabledMessage }) {
  return (
    <Card
      className={`result-panel result-panel--${variant} ${disabled ? "result-panel--disabled" : ""
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

  // CS2(서비스업)/CS3(도소매업)을 선택했고, 선택한 업종 중 실제로 mock 데이터라서
  // 비교 대상에서 빠진 게 있을 때만 이 목록이 채워진다. (변동성 과다로 제외된
  // 항목은 mock이 아니므로 이 안내에는 포함하지 않는다.)
  const mockExcludedItems =
    MOCK_NOTICE_MAJOR_CODES.includes(selectedMajor)
      ? (result?.noSalesData ?? [])
      : [];

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
        <h2>
          AI 예측 및 추천 결과 <Badge variant="warn">예측 데이터</Badge>
        </h2>
        <p className="ai-recommendation__desc">
          선택한 지역과 업종 데이터를 기반으로 분석한 결과이며, 실제 확정된 수치가
          아닌 AI 모델의 예측 데이터입니다.
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

            {mockExcludedItems.length > 0 && (
              <ResultPanel
                variant="info"
                icon={<FontAwesomeIcon icon={faCircleExclamation} />}
                title="예측 데이터 부족"
                items={mockExcludedItems.map((item) => ({
                  name: item.name,
                  description: "실측 매출 데이터가 부족하여 이번 비교에서 제외되었습니다.",
                  badge: "예측 데이터",
                }))}
              />
            )}
          </>
        )}
      </section>
    </div>
  );
}

export default AiRecommendation;
