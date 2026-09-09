import { useCallback, useEffect, useState } from "react";
import { useAuth } from "./useAuth.js";
import {
	fetchRecentSelections,
	saveRecentSelection,
	deleteRecentSelection,
} from "../api/recentSelectionsApi.js";

// 검색 엔진의 검색 이력과 동일한 방식으로, 사용자가 마지막으로 검색에 사용한
// 항목 조합을 최대 3개까지 저장해두고 다시 선택할 수 있게 한다.
// 비로그인 사용자는 브라우저 localStorage에, 로그인한 사용자는 계정별로 DB에 저장한다.
const MAX_ITEMS = 3;

function readStoredItems(storageKey) {
	try {
		const raw = localStorage.getItem(storageKey);
		return raw ? JSON.parse(raw) : [];
	} catch {
		return [];
	}
}

// 서버 응답({ id, label, payload })을 기존 프론트 코드가 쓰던
// 평탄화된 형태({ id, label, ...payload })로 변환
function toFlatItem(row) {
	return { id: row.id, label: row.label, ...row.payload };
}

export function useRecentSelections(storageKey) {
	const { isLoggedIn } = useAuth();
	const [items, setItems] = useState(() =>
		isLoggedIn ? [] : readStoredItems(storageKey),
	);

	useEffect(() => {
		if (!isLoggedIn) {
			setItems(readStoredItems(storageKey));
			return;
		}
		fetchRecentSelections(storageKey)
			.then((rows) => setItems(rows.map(toFlatItem)))
			.catch(() => setItems([]));
	}, [isLoggedIn, storageKey]);

	const addSelection = useCallback(
		(entry) => {
			if (isLoggedIn) {
				saveRecentSelection(storageKey, entry).then(() => {
					fetchRecentSelections(storageKey).then((rows) =>
						setItems(rows.map(toFlatItem)),
					);
				});
				return;
			}
			setItems((prev) => {
				const next = [
					{ ...entry, id: Date.now() },
					...prev.filter((item) => item.label !== entry.label),
				].slice(0, MAX_ITEMS);
				localStorage.setItem(storageKey, JSON.stringify(next));
				return next;
			});
		},
		[isLoggedIn, storageKey],
	);

	const removeSelection = useCallback(
		(id) => {
			if (isLoggedIn) {
				setItems((prev) => prev.filter((item) => item.id !== id));
				deleteRecentSelection(id).catch(() => {
					fetchRecentSelections(storageKey).then((rows) =>
						setItems(rows.map(toFlatItem)),
					);
				});
				return;
			}
			setItems((prev) => {
				const next = prev.filter((item) => item.id !== id);
				localStorage.setItem(storageKey, JSON.stringify(next));
				return next;
			});
		},
		[isLoggedIn, storageKey],
	);

	return { items, addSelection, removeSelection };
}
