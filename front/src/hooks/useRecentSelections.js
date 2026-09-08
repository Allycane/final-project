import { useCallback, useState } from "react";

// 검색 엔진의 검색 이력과 동일한 방식으로, 사용자가 마지막으로 검색에 사용한
// 항목 조합을 최대 3개까지 로컬에 저장해두고 다시 선택할 수 있게 한다.
const MAX_ITEMS = 3;

// TODO: FastAPI 연동 - 지금은 최근 선택 항목을 브라우저 localStorage에만 저장해서
// 기기/브라우저를 바꾸면 사라진다. 로그인한 사용자의 DB에 저장하려면 아래처럼
// axiosInstance의 api를 사용해 사용자 ID + storageKey(페이지 구분자) 기준으로
// 조회/저장/삭제하는 함수로 교체하고, 이 파일 아래쪽의 초기 조회(readStoredItems),
// addSelection, removeSelection 안의 localStorage 호출부를 각각 이 함수들로 바꿔주면 된다.
// import api from "../api/axiosInstance.js";
//
// async function fetchRecentSelections(userId, storageKey) {
//   // GET /api/recent-selections?user_id={userId}&page={storageKey} -> 최근 3개 반환
//   const { data } = await api.get("/api/recent-selections", {
//     params: { user_id: userId, page: storageKey },
//   });
//   return data; // [{ id, label, ...restoreValues }, ...]
// }
//
// async function saveRecentSelection(userId, storageKey, entry) {
//   // POST /api/recent-selections -> 사용자별/페이지별로 최대 3개까지만 저장하고,
//   // 초과분은 가장 오래된 항목부터 서버(DB)에서 삭제하도록 백엔드에서 처리
//   const { data } = await api.post("/api/recent-selections", {
//     user_id: userId,
//     page: storageKey,
//     ...entry,
//   });
//   return data;
// }
//
// async function deleteRecentSelection(userId, storageKey, id) {
//   // DELETE /api/recent-selections/{id}
//   await api.delete(`/api/recent-selections/${id}`, { params: { user_id: userId, page: storageKey } });
// }

function readStoredItems(storageKey) {
  try {
    const raw = localStorage.getItem(storageKey);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function useRecentSelections(storageKey) {
  const [items, setItems] = useState(() => readStoredItems(storageKey));
  // TODO: FastAPI 연동 - 위 localStorage 조회 대신 로그인한 사용자의 DB 데이터를
  // 불러오려면 아래처럼 fetchRecentSelections()를 사용해 마운트 시 서버에서 조회한다.
  // const { user } = useAuth();
  // useEffect(() => {
  //   if (!user) return;
  //   fetchRecentSelections(user.id, storageKey).then(setItems);
  // }, [user, storageKey]);

  const addSelection = useCallback(
    (entry) => {
      setItems((prev) => {
        const next = [
          { ...entry, id: Date.now() },
          ...prev.filter((item) => item.label !== entry.label),
        ].slice(0, MAX_ITEMS);
        localStorage.setItem(storageKey, JSON.stringify(next));
        // TODO: FastAPI 연동 - 위 localStorage 저장 대신(또는 함께) 사용자 ID 기준으로
        // 서버 DB에도 저장하려면 saveRecentSelection()을 사용한다.
        // if (user) {
        //   saveRecentSelection(user.id, storageKey, entry);
        // }
        return next;
      });
    },
    [storageKey],
  );

  const removeSelection = useCallback(
    (id) => {
      setItems((prev) => {
        const next = prev.filter((item) => item.id !== id);
        localStorage.setItem(storageKey, JSON.stringify(next));
        // TODO: FastAPI 연동 - 서버 DB에서도 함께 삭제하려면 deleteRecentSelection()을 사용한다.
        // if (user) {
        //   deleteRecentSelection(user.id, storageKey, id);
        // }
        return next;
      });
    },
    [storageKey],
  );

  return { items, addSelection, removeSelection };
}
