export const mockRecommendationResult = {
  recommended: {
    name: "치킨전문점",
    badge: "성장",
    description: "매출 +1.9%, 점포수 +1.0% 함께 늘어 신규 수요가 유입되는 업종입니다.",
  },
  notRecommended: [
    {
      name: "커피-음료",
      badge: "공급과잉",
      description: "매출은 -7.5%인데 점포수는 그대로라 경쟁이 치열해질 수 있어요.",
    },
    {
      name: "한식음식점",
      badge: "쇠퇴",
      description: "매출 -7.8%, 점포수 2%로 늘고 있어서 공급이 과잉될 수 있어요.",
    },
  ],
  reference: [
    {
      name: "일식음식점",
      badge: "참고",
      description:
        "매출도 늘고 있지만(+3.0%) 점포수도 함께 늘고 있어(+1.6%) 다음 분기에 잘될 가능성 38% 입니다.",
    },
  ],
};
