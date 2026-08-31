import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWandMagicSparkles } from "@fortawesome/free-solid-svg-icons";
import { getSalesAnalysis } from "../api/analysisApi.js";
import { mockRegions } from "../mocks/regions.js";
import { mockCategoryGroups } from "../mocks/categories.js";
import Select from "../components/common/Select.jsx";
import TextField from "../components/common/TextField.jsx";
import Button from "../components/common/Button.jsx";
import Card from "../components/common/Card.jsx";
import StatTile from "../components/common/StatTile.jsx";
import SalesLineChart from "../components/analysis/SalesLineChart.jsx";
import DistributionMapSection from "../components/analysis/DistributionMapSection.jsx";
import "../styles/AiAnalysis.css";

function AiAnalysis() {
  const [region, setRegion] = useState("");
  const [majorCategory, setMajorCategory] = useState("");
  const [minorCategory, setMinorCategory] = useState("");
  const [targetSales, setTargetSales] = useState("");
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isMapExpanded, setIsMapExpanded] = useState(false);

  const minorOptions =
    mockCategoryGroups.find((group) => group.code === majorCategory)?.children ?? [];

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const data = await getSalesAnalysis({
        region,
        majorCategory,
        minorCategory,
        targetSales,
      });
      setResult(data);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`container ai-analysis ${isMapExpanded ? "ai-analysis--expanded" : ""}`.trim()}>
      <div className="ai-analysis__hero">
        <h1>AI 매출 분석</h1>
        <p>
          지역과 업종, 목표 매출을 입력하면 학습된 데이터를 기반으로
          <br />
          평균 매출과 미래 매출 전망, 목표 달성 가능성을 분석합니다.
        </p>
      </div>

      <Card className="ai-analysis__condition">
        <h2>분석 조건 설정</h2>
        <p className="ai-analysis__desc">분석에 필요한 조건을 선택한 후 AI 매출 분석을 시작하세요.</p>

        <div className="ai-analysis__condition-grid">
          <Select
            label="지역 (자치구)"
            id="region"
            placeholder="자치구를 선택하세요"
            options={mockRegions}
            value={region}
            onChange={(e) => setRegion(e.target.value)}
          />
          <Select
            label="업종 대분류"
            id="majorCategory"
            placeholder="대분류를 선택하세요"
            options={mockCategoryGroups}
            value={majorCategory}
            onChange={(e) => {
              setMajorCategory(e.target.value);
              setMinorCategory("");
            }}
          />
          <Select
            label="업종 소분류"
            id="minorCategory"
            placeholder="소분류를 선택하세요"
            options={minorOptions}
            value={minorCategory}
            onChange={(e) => setMinorCategory(e.target.value)}
          />
          <TextField
            label="분기별 목표 매출액 (만원)"
            id="targetSales"
            type="number"
            placeholder="예: 5,000"
            value={targetSales}
            onChange={(e) => setTargetSales(e.target.value)}
          />
        </div>

        <Button block onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? "분석 중..." : "AI 매출 분석 시작하기 →"}
        </Button>
      </Card>

      <section className="ai-analysis__result">
        <h2>AI 분석 결과</h2>
        <p className="ai-analysis__desc">선택한 지역과 업종, 목표 매출을 기반으로 분석된 결과입니다.</p>

        <div className="ai-analysis__stat-grid">
          <StatTile
            label="평균 매출"
            value={result?.averageSales}
            hint={result ? "학습 데이터 기반" : "분석 결과 대기 중"}
          />
          <StatTile
            label="목표 대비"
            value={result?.vsTarget}
            hint={result ? "목표 매출 대비 비율" : "목표 매출 입력 후 계산"}
          />
          <StatTile
            label="AI 예측 매출"
            value={result?.predictedSales}
            hint="학습 데이터 기반 전망"
          />
          <StatTile
            label="목표 달성 확률"
            value={result?.targetAchieveRate}
            hint="예측 결과로 계산"
          />
        </div>

        <Card className="ai-analysis__chart">
          <h3>분기별 매출 추이 및 AI 예측</h3>
          <p className="ai-analysis__desc">단위: 만원</p>
          {result ? (
            <SalesLineChart data={result.quarters} />
          ) : (
            <div className="ai-analysis__chart-placeholder">
              분석을 시작하면 매출 추이 그래프가 표시됩니다.
            </div>
          )}
        </Card>

        <Card className="ai-analysis__insight">
          <div className="ai-analysis__insight-icon">
            <FontAwesomeIcon icon={faWandMagicSparkles} />
          </div>
          <div>
            <h3>AI 종합 인사이트</h3>
            <p>
              {result
                ? result.insight
                : "분석 완료 후 지역별 상권 특성, 매출 흐름, 목표 달성 가능성에 대한 AI 종합 의견이 이 영역에 출력됩니다."}
            </p>
          </div>
        </Card>

        <Button block onClick={() => setIsMapExpanded((prev) => !prev)}>
          {isMapExpanded ? "지도 닫기 ✕" : "지도로 분포 확인 →"}
        </Button>

        {isMapExpanded && <DistributionMapSection />}
      </section>
    </div>
  );
}

export default AiAnalysis;
