import { useMemo, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMagnifyingGlass, faPlus, faXmark } from "@fortawesome/free-solid-svg-icons";
import { mockCategoryGroups, mockStoreTypes } from "../../mocks/categories.js";
import { mockRegions } from "../../mocks/regions.js";

const TABS = [
  { key: "category", label: "업종 추가" },
  { key: "region", label: "지역 추가" },
  { key: "storeType", label: "매장 형태 추가" },
];

const ALL_CATEGORY_NAMES = mockCategoryGroups.flatMap((group) =>
  group.children.map((child) => child.name)
);
const ALL_REGION_NAMES = mockRegions.map((region) => region.name);
const ALL_STORE_TYPE_NAMES = mockStoreTypes.map((storeType) => storeType.name);

const SOURCE_BY_TAB = {
  category: ALL_CATEGORY_NAMES,
  region: ALL_REGION_NAMES,
  storeType: ALL_STORE_TYPE_NAMES,
};

function AddItemModal({ initialTab, selected, limits, onAdd, onClose }) {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [searchTerm, setSearchTerm] = useState("");

  const selectedNames = selected[activeTab] ?? [];
  const limit = limits[activeTab];
  const isLimitReached = selectedNames.length >= limit;
  const hasSearch = activeTab !== "storeType";

  const items = useMemo(() => {
    const source = SOURCE_BY_TAB[activeTab].filter((name) => !selectedNames.includes(name));
    if (!hasSearch || !searchTerm.trim()) return source;
    return source.filter((name) => name.includes(searchTerm.trim()));
  }, [activeTab, searchTerm, hasSearch, selectedNames]);

  const handleTabChange = (tabKey) => {
    setActiveTab(tabKey);
    setSearchTerm("");
  };

  return (
    <div className="add-item-modal__backdrop" onClick={onClose}>
      <div className="add-item-modal" onClick={(event) => event.stopPropagation()}>
        <div className="add-item-modal__header">
          <h2>항목 추가</h2>
          <button
            type="button"
            className="add-item-modal__close"
            aria-label="닫기"
            onClick={onClose}
          >
            <FontAwesomeIcon icon={faXmark} />
          </button>
        </div>

        <div className="add-item-modal__tabs">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              type="button"
              className={`add-item-modal__tab ${activeTab === tab.key ? "is-active" : ""}`.trim()}
              onClick={() => handleTabChange(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {hasSearch && (
          <div className="add-item-modal__search">
            <input
              type="text"
              placeholder="검색어를 입력하세요"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />
            <FontAwesomeIcon icon={faMagnifyingGlass} />
          </div>
        )}

        <p className="add-item-modal__label">
          {activeTab === "storeType" ? "매장 형태" : "추천 항목"}
        </p>

        <div className="add-item-modal__grid">
          {items.length === 0 && (
            <p className="add-item-modal__empty">검색 결과가 없습니다.</p>
          )}
          {items.map((name) => (
            <button
              key={name}
              type="button"
              className="add-item-modal__chip"
              disabled={isLimitReached}
              onClick={() => onAdd(activeTab, name)}
            >
              <span>{name}</span>
              <FontAwesomeIcon icon={faPlus} />
            </button>
          ))}
        </div>

        <div className="add-item-modal__footer">
          {isLimitReached ? (
            <span>최대 {limit}개까지 선택할 수 있습니다.</span>
          ) : (
            hasSearch && <span>원하는 항목이 없을 경우 검색을 통해 더 많은 항목을 찾아보세요.</span>
          )}
        </div>
      </div>
    </div>
  );
}

export default AddItemModal;
