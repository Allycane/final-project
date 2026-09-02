import { useState, useEffect } from "react"; // useEffect 추가
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { useAuth } from "../hooks/useAuth.js";
// import { mockUser } from "../mocks/users.js";
// -> 실제 데이터가 들어가도록
import { updateMyProfile } from "../api/userApi.js";
import AddItemModal from "../components/mypage/AddItemModal.jsx";
import Card from "../components/common/Card.jsx";
import TextField from "../components/common/TextField.jsx";
import Button from "../components/common/Button.jsx";
import Tag from "../components/common/Tag.jsx";
import "../styles/Mypage.css";

const LIMITS = { category: 10, region: 5, storeType: 5 };

// function buildInitialState(baseUser) {
//   return {
//     form: {
//       name: baseUser.name ?? "",
//       phone: baseUser.phone ?? "",
//       email: baseUser.email ?? "",
//       password: "",
//       passwordConfirm: "",
//     },
//     categories: baseUser.interests?.categories ?? [],
//     regions: baseUser.interests?.regions ?? [],
//     storeTypes: baseUser.interests?.storeTypes ?? [],
//   };
// }
function buildInitialState(baseUser) {
	const storeTypes = Array.isArray(baseUser.store_types)
		? baseUser.store_types
		: [];

	return {
		form: {
			name: baseUser.name ?? "",
			phone: baseUser.phone ?? "",
			email: baseUser.email ?? "",
			password: "",
			passwordConfirm: "",
		},
		categories: baseUser.categories ?? [],
		regions: baseUser.regions ?? [],
		storeTypes,
	};
}

function InterestSection({
	title,
	hint,
	addLabel,
	items,
	onRemove,
	onAddClick,
}) {
	return (
		<div className="mypage__interest-section">
			<div className="mypage__section-head">
				<div>
					<h3>{title}</h3>
					<p className="mypage__hint">{hint}</p>
				</div>
				<button type="button" className="mypage__add-btn" onClick={onAddClick}>
					<FontAwesomeIcon icon={faPlus} /> {addLabel}
				</button>
			</div>

			<div className="mypage__tag-list">
				{items.length === 0 && (
					<span className="mypage__empty">선택된 항목이 없습니다.</span>
				)}
				{items.map((name) => (
					<Tag key={name} onRemove={() => onRemove(name)}>
						{name}
					</Tag>
				))}
			</div>
		</div>
	);
}

function Mypage() {
	const { user, login } = useAuth();
	//   const baseUser = user ?? mockUser;
	const baseUser = user ?? {};

	const navigate = useNavigate();
	const [state, setState] = useState(() => buildInitialState(baseUser));
	useEffect(() => {
		if (user) {
			setState(buildInitialState(user));
		}
	}, [user]);
	const [activeModalTab, setActiveModalTab] = useState(null);
	const [isSaving, setIsSaving] = useState(false);
	const [error, setError] = useState("");

	const { form, categories, regions, storeTypes } = state;

	const listKeyByTab = {
		category: "categories",
		region: "regions",
		storeType: "storeTypes",
	};

	const handleFieldChange = (event) => {
		const { name, value } = event.target;
		setState((prev) => ({ ...prev, form: { ...prev.form, [name]: value } }));
	};

	const removeItem = (tab, name) => {
		const key = listKeyByTab[tab];
		setState((prev) => ({
			...prev,
			[key]: prev[key].filter((item) => item !== name),
		}));
	};

	const addItem = (tab, name) => {
		const key = listKeyByTab[tab];
		setState((prev) => {
			if (prev[key].includes(name) || prev[key].length >= LIMITS[tab])
				return prev;
			return { ...prev, [key]: [...prev[key], name] };
		});
	};

	const handleCancel = () => {
		navigate("/");
	};

	const handleSave = async () => {
		if (form.password && form.password !== form.passwordConfirm) {
			setError("비밀번호가 일치하지 않습니다.");
			return;
		}

		setError("");
		setIsSaving(true);
		try {
			const updated = await updateMyProfile({
				name: form.name,
				phone: form.phone,
				email: form.email,
				password: form.password || undefined,
				categories,
				regions,
				store_types: storeTypes,
			});
			login(updated);
			navigate("/");
		} finally {
			setIsSaving(false);
		}
	};

	return (
		<div className="container mypage">
			<h1>사용자 정보 수정</h1>
			<p className="mypage__desc">
				회원님의 정보를 관리하고 관심 정보를 수정할 수 있습니다.
			</p>

			<Card className="mypage__section">
				<h2>기본 정보</h2>
				<div className="mypage__basic-grid">
					<TextField
						label="이름"
						id="name"
						name="name"
						value={form.name}
						onChange={handleFieldChange}
					/>
					<TextField
						label="전화번호"
						id="phone"
						name="phone"
						type="tel"
						value={form.phone}
						onChange={handleFieldChange}
					/>
					<TextField
						label="이메일"
						id="email"
						name="email"
						type="email"
						value={form.email}
						onChange={handleFieldChange}
					/>
					<div className="mypage__password-field">
						<TextField
							label="비밀번호 변경"
							id="password"
							name="password"
							type="password"
							placeholder="새 비밀번호 입력 (8자 이상)"
							value={form.password}
							onChange={handleFieldChange}
						/>
						<p className="mypage__field-hint">
							영문, 숫자, 특수문자를 포함한 8자 이상을 권장합니다.
						</p>
					</div>
					<TextField
						label="비밀번호 확인"
						id="passwordConfirm"
						name="passwordConfirm"
						type="password"
						placeholder="새 비밀번호 다시 입력"
						value={form.passwordConfirm}
						onChange={handleFieldChange}
					/>
				</div>
				{error && <p className="mypage__error">{error}</p>}
			</Card>

			<Card className="mypage__section">
				<h2>관심 정보</h2>

				<InterestSection
					title="관심 업종"
					hint={`최대 ${LIMITS.category}개까지 선택할 수 있습니다.`}
					addLabel="업종 추가"
					items={categories}
					onRemove={(name) => removeItem("category", name)}
					onAddClick={() => setActiveModalTab("category")}
				/>
				<hr className="mypage__divider" />
				<InterestSection
					title="관심 지역"
					hint={`최대 ${LIMITS.region}개까지 선택할 수 있습니다.`}
					addLabel="지역 추가"
					items={regions}
					onRemove={(name) => removeItem("region", name)}
					onAddClick={() => setActiveModalTab("region")}
				/>
				<hr className="mypage__divider" />
				<InterestSection
					title="매장 형태"
					hint={`최대 ${LIMITS.storeType}개까지 선택할 수 있습니다.`}
					addLabel="형태 추가"
					items={storeTypes}
					onRemove={(name) => removeItem("storeType", name)}
					onAddClick={() => setActiveModalTab("storeType")}
				/>
			</Card>

			<div className="mypage__actions">
				<Button variant="outline" onClick={handleCancel} disabled={isSaving}>
					취소
				</Button>
				<Button onClick={handleSave} disabled={isSaving}>
					{isSaving ? "저장 중..." : "변경 사항 저장"}
				</Button>
			</div>

			{activeModalTab && (
				<AddItemModal
					initialTab={activeModalTab}
					selected={{
						category: categories,
						region: regions,
						storeType: storeTypes,
					}}
					limits={LIMITS}
					onAdd={addItem}
					onClose={() => setActiveModalTab(null)}
				/>
			)}
		</div>
	);
}

export default Mypage;
