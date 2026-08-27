// server/data 서비스_업종_코드(대/중/소분류) 체계를 참고한 mock 업종 카테고리
export const mockCategoryGroups = [
  {
    code: "food",
    name: "외식업",
    children: [
      { code: "korean", name: "한식 / 중식 / 일식 / 양식" },
      { code: "bakery", name: "제과 / 베이커리" },
      { code: "fastfood", name: "패스트푸드 / 분식" },
      { code: "pub", name: "주점" },
      { code: "cafe", name: "카페 / 음료" },
    ],
  },
  {
    code: "service",
    name: "서비스업",
    children: [
      { code: "education", name: "교육" },
      { code: "medical", name: "의료" },
      { code: "professional", name: "전문 (법률/회계)" },
      { code: "leisure", name: "레저 / 오락" },
      { code: "life", name: "수리 / 미용 / 생활" },
      { code: "realestate", name: "부동산 / 숙박 / 기타" },
    ],
  },
  {
    code: "retail",
    name: "도·소매업",
    children: [
      { code: "grocery", name: "식품 소매" },
      { code: "fashion", name: "의류 / 잡화" },
      { code: "health", name: "생활 / 건강" },
      { code: "culture", name: "문화 / 취미" },
      { code: "electronics", name: "가전 / 전자 / IT" },
      { code: "furniture", name: "가구 / 인테리어 / 자동차" },
    ],
  },
];

export const mockSubCategoriesByParent = {
  korean: ["한식", "일식", "중식", "양식", "분식", "키즈/디저트"],
};

export const mockStoreTypes = [
  { code: "street", name: "길거리 매장" },
  { code: "mall", name: "상가/쇼핑몰 입점" },
  { code: "delivery", name: "배달 전문(무점포)" },
  { code: "franchise", name: "프랜차이즈" },
];
