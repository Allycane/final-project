import "../../styles/KakaoMap.css";

// TODO: 카카오맵 API 연동 필요
// 1) front/index.html <head>에 다음 스크립트 추가
//    <script src="//dapi.kakao.com/v2/maps/sdk.js?appkey=REST_API_KEY&autoload=false"></script>
//    (REST_API_KEY는 .env의 VITE_KAKAO_MAP_KEY 값을 build 시점에 주입)
// 2) 이 컴포넌트를 useRef + useEffect로 감싸서
//    kakao.maps.load(() => {
//      const map = new kakao.maps.Map(containerRef.current, { center: new kakao.maps.LatLng(center.lat, center.lng), level: 5 });
//      points.forEach((point) => new kakao.maps.Marker({ position: new kakao.maps.LatLng(point.lat, point.lng), map }));
//    })
//    형태로 지도를 초기화하고, 아래 placeholder 마크업을 실제 지도 컨테이너로 교체합니다.
// 3) mapApi.getDistribution() 결과(mock 좌표)를 실제 kakao.maps.Marker로 교체합니다.
function KakaoMap({ center, points = [] }) {
  return (
    <div className="kakao-map-placeholder">
      <div className="kakao-map-placeholder__badge">Kakao Map API (연동 전 placeholder)</div>
      <div className="kakao-map-placeholder__center">
        중심 좌표: {center?.lat}, {center?.lng}
      </div>
      <ul className="kakao-map-placeholder__points">
        {points.map((point) => (
          <li key={point.id}>
            <span className="kakao-map-placeholder__marker" />
            {point.name} · {point.category} · {point.count}개
          </li>
        ))}
      </ul>
    </div>
  );
}

export default KakaoMap;
