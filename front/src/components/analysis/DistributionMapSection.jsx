import { useEffect, useMemo, useState } from "react";
import { getDistribution } from "../../api/mapApi.js";
import { mockCategoryGroups } from "../../mocks/categories.js";
import KakaoMap from "../map/KakaoMap.jsx";
import Select from "../common/Select.jsx";
import Tag from "../common/Tag.jsx";
import Button from "../common/Button.jsx";
import Card from "../common/Card.jsx";
import "../../styles/DistributionMapSection.css";

const DISTRIBUTION_RADIUS_M = 500;
const MAX_MARKERS = 30;

function DistributionMapSection({
	region,
	majorCategory: initialMajorCategory,
	minorCategory: initialMinorCategory,
	targetSales,
}) {
	const [mapMajorCategory, setMapMajorCategory] = useState(
		initialMajorCategory ?? "",
	);
	const [selectedSub, setSelectedSub] = useState(
		initialMinorCategory ? [initialMinorCategory] : [],
	);
	const [pendingSub, setPendingSub] = useState("");
	const [mapData, setMapData] = useState(null);
	const [mapCenter, setMapCenter] = useState(null);
	const [isLoading, setIsLoading] = useState(false);

	const subOptions = useMemo(
		() =>
			mockCategoryGroups.find((group) => group.code === mapMajorCategory)
				?.children ?? [],
		[mapMajorCategory],
	);

	const allSubOptions = useMemo(
		() => mockCategoryGroups.flatMap((group) => group.children),
		[],
	);

	const subName = (code) =>
		allSubOptions.find((item) => item.code === code)?.name ?? code;

	useEffect(() => {
		if (
			!region ||
			!initialMajorCategory ||
			!initialMinorCategory ||
			!targetSales
		) {
			setMapData(null);
			setMapCenter(null);
			return;
		}

		setMapMajorCategory(initialMajorCategory);
		setSelectedSub([initialMinorCategory]);
		setPendingSub("");

		const loadInitialDistribution = async () => {
			setIsLoading(true);

			try {
				const data = await getDistribution({
					region,
					majorCategory: initialMajorCategory,
					subCategories: [initialMinorCategory],
					radius: DISTRIBUTION_RADIUS_M,
					markerLimit: MAX_MARKERS,
				});

				setMapData(data);
				setMapCenter(data?.center ?? null);
			} catch (error) {
				console.error("초기 지도 분포 조회 실패:", error);
				setMapData(null);
			} finally {
				setIsLoading(false);
			}
		};

		loadInitialDistribution();
	}, [region, initialMajorCategory, initialMinorCategory, targetSales]);

	const toggleSub = (code) => {
		setSelectedSub((prev) =>
			prev.includes(code)
				? prev.filter((item) => item !== code)
				: [...prev, code],
		);
	};

	const addSub = () => {
		if (!pendingSub) return;

		setSelectedSub((prev) =>
			prev.includes(pendingSub) ? prev : [...prev, pendingSub],
		);
		setPendingSub("");
	};

	const removeSub = (code) => {
		setSelectedSub((prev) => prev.filter((item) => item !== code));
	};

	const handleShowDistribution = async () => {
		if (!region) return;

		const center = mapCenter ?? mapData?.center;
		setIsLoading(true);

		try {
			const data = await getDistribution({
				region,
				majorCategory: mapMajorCategory || undefined,
				subCategories: selectedSub,
				radius: DISTRIBUTION_RADIUS_M,
				centerLat: center?.lat,
				centerLng: center?.lng,
				markerLimit: MAX_MARKERS,
			});

			setMapData(data);
			setMapCenter(data?.center ?? center ?? null);
		} catch (error) {
			console.error("지도 분포 조회 실패:", error);
		} finally {
			setIsLoading(false);
		}
	};

	if (!region || !initialMajorCategory || !initialMinorCategory) {
		return (
			<section className="distribution-map">
				<Card>
					<p>매출 분석 조건 선택한 후 지도를 이용할 수 있습니다.</p>
				</Card>
			</section>
		);
	}

	return (
		<section className="distribution-map">
			<h2>지역별 분포 상세 지도</h2>
			<p className="distribution-map__desc">
				매출 분석에서 선택한 조건으로 처음 표시되며, 이후에는 지도 안에서 업종과
				위치를 자유롭게 바꿀 수 있습니다. 지도를 옮긴 뒤 버튼을 누르면 자치구가
				바뀌었더라도 이동한 위치를 기준으로 다시 조회됩니다.
			</p>

			<Card className="distribution-map__layout">
				<div className="distribution-map__map">
					<KakaoMap
						center={mapData?.center}
						points={mapData?.points ?? []}
						radius={DISTRIBUTION_RADIUS_M}
						maxMarkers={MAX_MARKERS}
						onCenterChanged={setMapCenter}
					/>
					<div className="distribution-map__legend">
						<span className="distribution-map__legend-dot" aria-hidden="true" />
						조회 기준 중심 · 반경 {DISTRIBUTION_RADIUS_M}m · 가까운 순 최대{" "}
						{MAX_MARKERS}곳
					</div>
					{isLoading && (
						<div className="distribution-map__loading">
							분포 데이터를 불러오는 중...
						</div>
					)}
				</div>

				<div className="distribution-map__panel">
					<Select
						label="업종 대분류"
						id="distribution-majorCategory"
						options={mockCategoryGroups}
						value={mapMajorCategory}
						onChange={(e) => {
							setMapMajorCategory(e.target.value);
							setPendingSub("");
							setSelectedSub([]);
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
								<span
									style={{
										fontSize: 12,
										color: "var(--color-text-muted-2)",
									}}
								>
									선택된 업종이 없습니다.
								</span>
							)}

							{selectedSub.map((code) => (
								<Tag key={code} onRemove={() => removeSub(code)}>
									{subName(code)}
								</Tag>
							))}
						</div>
					</div>

					<Button block onClick={handleShowDistribution} disabled={isLoading}>
						지도에서 선택한 업종 분포 보기
					</Button>
					{/* [수정 끝] "현재 지도 위치에서 분포 다시 보기" 버튼 제거됨 */}
				</div>
			</Card>
		</section>
	);
}

export default DistributionMapSection;
