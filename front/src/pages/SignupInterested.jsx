import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { signupInterests } from "../api/authApi.js";
import { useAuth } from "../hooks/useAuth.js";
import { mockCategoryGroups, mockStoreTypes } from "../mocks/categories.js";
import { mockRegions } from "../mocks/regions.js";
import { SIGNUP_STEPS } from "../constants/signup.js";
import StepIndicator from "../components/common/StepIndicator.jsx";
import CategoryToggleGroup from "../components/common/CategoryToggleGroup.jsx";
import Select from "../components/common/Select.jsx";
import Button from "../components/common/Button.jsx";
import Card from "../components/common/Card.jsx";
import Tag from "../components/common/Tag.jsx";
import "../styles/Signup.css";

function SignupInterested() {
	const navigate = useNavigate();
	const location = useLocation();
	const { login } = useAuth();
	const basicInfo = location.state ?? {};

	const [selectedCategories, setSelectedCategories] = useState([]);
	const [selectedRegions, setSelectedRegions] = useState([]);
	const [regionToAdd, setRegionToAdd] = useState("");
	const [selectedStoreTypes, setSelectedStoreTypes] = useState([]);

	const toggleStoreType = (code) => {
		setSelectedStoreTypes((prev) =>
			prev.includes(code)
				? prev.filter((item) => item !== code)
				: [...prev, code],
		);
	};
	const [isSubmitting, setIsSubmitting] = useState(false);

	const allCategoryOptions = mockCategoryGroups.flatMap(
		(group) => group.children,
	);

	const toggleCategory = (code) => {
		setSelectedCategories((prev) =>
			prev.includes(code)
				? prev.filter((item) => item !== code)
				: [...prev, code],
		);
	};

	const addRegion = () => {
		if (regionToAdd && !selectedRegions.includes(regionToAdd)) {
			setSelectedRegions((prev) => [...prev, regionToAdd]);
		}
		setRegionToAdd("");
	};

	const removeRegion = (code) => {
		setSelectedRegions((prev) => prev.filter((item) => item !== code));
	};

	const categoryName = (code) =>
		allCategoryOptions.find((c) => c.code === code)?.name ?? code;
	const regionName = (code) =>
		mockRegions.find((r) => r.code === code)?.name ?? code;
	const storeTypeName = (code) =>
		mockStoreTypes.find((s) => s.code === code)?.name ?? code;

	const handleSubmit = async () => {
		setIsSubmitting(true);
		try {
			const payload = {
				...basicInfo,
				categories: selectedCategories.map(categoryName),
				regions: selectedRegions.map(regionName),
				storeTypes: selectedStoreTypes.map(storeTypeName), // storeType → storeTypes로 변경
			};
			const user = await signupInterests(payload);
			login(user);
			navigate("/");
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<div className="container signup-page">
			<h1 className="signup-page__title">회원가입</h1>
			<StepIndicator steps={SIGNUP_STEPS} currentStep={2} />

			<Card className="signup-page__panel">
				<div className="signup-interest__grid">
					<aside className="signup-interest__summary">
						<h3>
							{basicInfo.name ? `${basicInfo.name}님의 정보` : "나의 정보"}
						</h3>

						<p className="signup-interest__summary-label">관심 업종</p>
						<div className="signup-interest__tag-list">
							{selectedCategories.length === 0 && (
								<span
									style={{ fontSize: 12, color: "var(--color-text-muted-2)" }}
								>
									선택된 업종이 없습니다.
								</span>
							)}
							{selectedCategories.map((code) => (
								<Tag key={code} onRemove={() => toggleCategory(code)}>
									{categoryName(code)}
								</Tag>
							))}
						</div>

						<p className="signup-interest__summary-label">관심 지역</p>
						<div className="signup-interest__tag-list">
							{selectedRegions.length === 0 && (
								<span
									style={{ fontSize: 12, color: "var(--color-text-muted-2)" }}
								>
									선택된 지역이 없습니다.
								</span>
							)}
							{selectedRegions.map((code) => (
								<Tag key={code} onRemove={() => removeRegion(code)}>
									{regionName(code)}
								</Tag>
							))}
						</div>

						<p className="signup-interest__summary-label">매장 형태</p>
						<div className="signup-interest__tag-list">
							{selectedStoreTypes.length === 0 && (
								<span
									style={{ fontSize: 12, color: "var(--color-text-muted-2)" }}
								>
									선택된 매장 형태가 없습니다.
								</span>
							)}
							{selectedStoreTypes.map((code) => (
								<Tag key={code} onRemove={() => toggleStoreType(code)}>
									{storeTypeName(code)}
								</Tag>
							))}
						</div>
					</aside>

					<div className="signup-interest__form">
						<h2>관심 정보 선택</h2>
						<p className="signup-page__desc">
							관심 업종과 창업 선호 정보를 선택하면 더 정확한 창업 정보를 받을
							수 있어요.
						</p>

						<section className="signup-interest__section">
							<h4>1. 관심 업종 선택</h4>
							<p className="signup-page__desc">복수 선택 가능</p>

							{mockCategoryGroups.map((group) => (
								<div className="signup-interest__group" key={group.code}>
									<p className="signup-interest__group-title">{group.name}</p>
									<CategoryToggleGroup
										options={group.children}
										selected={selectedCategories}
										onToggle={toggleCategory}
									/>
								</div>
							))}
						</section>

						<section className="signup-interest__section">
							<h4>2. 창업 선호 지역</h4>
							<div className="signup-interest__region-row">
								<Select
									id="regionToAdd"
									placeholder="지역을 선택해주세요"
									options={mockRegions}
									value={regionToAdd}
									onChange={(e) => setRegionToAdd(e.target.value)}
								/>
								<Button variant="outline" onClick={addRegion}>
									추가
								</Button>
							</div>
						</section>

						<section className="signup-interest__section">
							<h4>3. 매장 형태</h4>
							<p className="signup-page__desc">복수 선택 가능</p>
							<CategoryToggleGroup
								options={mockStoreTypes}
								selected={selectedStoreTypes}
								onToggle={toggleStoreType}
							/>
						</section>

						<div className="signup-interest__actions">
							<Button block disabled={isSubmitting} onClick={handleSubmit}>
								{isSubmitting ? "처리 중..." : "회원가입 완료"}
							</Button>
						</div>
					</div>
				</div>
			</Card>
		</div>
	);
}

export default SignupInterested;
