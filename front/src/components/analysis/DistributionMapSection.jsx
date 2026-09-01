import { useEffect, useState } from "react";
import { getDistribution } from "../../api/mapApi.js";
import { mockCategoryGroups } from "../../mocks/categories.js";
import KakaoMap from "../map/KakaoMap.jsx";
import Select from "../common/Select.jsx";
import Tag from "../common/Tag.jsx";
import Button from "../common/Button.jsx";
import Card from "../common/Card.jsx";
import "../../styles/DistributionMapSection.css";

// "지도로 분포 확인" 클릭 시 별도 라우팅 페이지로 이동하지 않고,
// AiAnalysis 페이지 내에서 반응형으로 확장되어 보여지는 지도 섹션
function DistributionMapSection() {
  const [majorCategory, setMajorCategory] = useState(mockCategoryGroups[0]?.code ?? "");
  const [selectedSub, setSelectedSub] = useState([]);
  const [pendingSub, setPendingSub] = useState("");
  const [mapData, setMapData] = useState(null);

  const subOptions = mockCategoryGroups.find((g) => g.code === majorCategory)?.children ?? [];

  useEffect(() => {
    getDistribution({}).then(setMapData);
  }, []);

  const toggleSub = (code) => {
    setSelectedSub((prev) =>
      prev.includes(code) ? prev.filter((item) => item !== code) : [...prev, code]
    );
  };

  const addSub = () => {
    if (!pendingSub) return;
    setSelectedSub((prev) => (prev.includes(pendingSub) ? prev : [...prev, pendingSub]));
    setPendingSub("");
  };

  const subName = (code) => subOptions.find((item) => item.code === code)?.name ?? code;

  const handleShowDistribution = async () => {
    const data = await getDistribution({ majorCategory, subCategories: selectedSub });
    setMapData(data);
  };

  return (
    <section className="distribution-map">
      <h2>지역별 분포 상세 지도</h2>
      <p className="distribution-map__desc">선택한 지역과 업종의 분포를 지도에서 확인해보세요.</p>

      <Card className="distribution-map__layout">
        <div className="distribution-map__map">
          <KakaoMap center={mapData?.center} points={mapData?.points ?? []} />
        </div>

        <div className="distribution-map__panel">
          <Select
            label="업종 대분류"
            id="distribution-majorCategory"
            options={mockCategoryGroups}
            value={majorCategory}
            onChange={(e) => {
              setMajorCategory(e.target.value);
              setSelectedSub([]);
              setPendingSub("");
            }}
          />

          <div className="field">
            <span className="field-label">세부 업종 선택</span>
            <div className="distribution-map__sub-picker">
              <Select
                id="distribution-subCategory"
                placeholder="세부 업종을 선택하세요"
                options={subOptions}
                value={pendingSub}
                onChange={(e) => setPendingSub(e.target.value)}
              />
              <Button onClick={addSub} disabled={!pendingSub}>
                선택
              </Button>
            </div>
          </div>

          <div className="field">
            <span className="field-label">선택된 업종 리스트</span>
            <div className="distribution-map__selected-list">
              {selectedSub.length === 0 && (
                <span style={{ fontSize: 12, color: "var(--color-text-muted-2)" }}>
                  선택된 업종이 없습니다.
                </span>
              )}
              {selectedSub.map((code) => (
                <Tag key={code} onRemove={() => toggleSub(code)}>
                  {subName(code)}
                </Tag>
              ))}
            </div>
          </div>

          <Button block onClick={handleShowDistribution}>
            지도에서 선택한 업종 분포 보기
          </Button>
        </div>
      </Card>
    </section>
  );
}

export default DistributionMapSection;
