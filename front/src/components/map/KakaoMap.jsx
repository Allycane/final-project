// import "../../styles/KakaoMap.css";

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

// function KakaoMap({ center, points = [] }) {
//   return (
//     <div className="kakao-map-placeholder">
//       <div className="kakao-map-placeholder__badge">Kakao Map API (연동 전 placeholder)</div>
//       <div className="kakao-map-placeholder__center">
//         중심 좌표: {center?.lat}, {center?.lng}
//       </div>
//       <ul className="kakao-map-placeholder__points">
//         {points.map((point) => (
//           <li key={point.id}>
//             <span className="kakao-map-placeholder__marker" />
//             {point.name} · {point.category} · {point.count}개
//           </li>
//         ))}
//       </ul>
//     </div>
//   );
// }

// export default KakaoMap;

import { useEffect, useRef } from "react";
import "../../styles/KakaoMap.css";

function KakaoMap({ center, points = [] }) {
	const containerRef = useRef(null);
	const mapRef = useRef(null);
	const markersRef = useRef([]);

	useEffect(() => {
		// 카카오 SDK가 아직 로드되지 않았거나(index.html 스크립트 미반영),
		// 지도를 그릴 DOM이 아직 없으면 실행하지 않음
		if (!window.kakao || !containerRef.current) return;

		window.kakao.maps.load(() => {
			// center가 아직 없을 경우(초기 로딩 시점)를 대비한 기본 좌표
			const defaultCenter = center ?? { lat: 37.4979, lng: 127.0276 };

			// 지도가 이미 생성되어 있으면 재사용하고 중심 좌표만 갱신,
			// 처음이면 새로 생성 (매번 새 지도를 만들지 않도록 함)
			if (!mapRef.current) {
				mapRef.current = new window.kakao.maps.Map(containerRef.current, {
					center: new window.kakao.maps.LatLng(
						defaultCenter.lat,
						defaultCenter.lng,
					),
					level: 5,
				});
			} else {
				mapRef.current.setCenter(
					new window.kakao.maps.LatLng(defaultCenter.lat, defaultCenter.lng),
				);
			}

			// 이전에 찍혀 있던 마커들을 전부 지도에서 제거
			markersRef.current.forEach((marker) => marker.setMap(null));
			markersRef.current = [];

			// 현재는 mock 데이터 기반 mockMapPoints(mockPoints.js)
			points.forEach((point) => {
				const marker = new window.kakao.maps.Marker({
					position: new window.kakao.maps.LatLng(point.lat, point.lng),
					map: mapRef.current,
				});
				markersRef.current.push(marker); // 다음번 정리를 위해 저장

				// 마커에 마우스를 올리면 매장명/업종/개수 정보 표시
				const infowindow = new window.kakao.maps.InfoWindow({
					content: `<div style="padding:6px 10px;font-size:12px;">${point.name} · ${point.category} · ${point.count}개</div>`,
				});

				window.kakao.maps.event.addListener(marker, "mouseover", () => {
					infowindow.open(mapRef.current, marker);
				});
				window.kakao.maps.event.addListener(marker, "mouseout", () => {
					infowindow.close();
				});
			});
		});
	}, [center, points]);

	return <div ref={containerRef} className="kakao-map-container" />;
}

export default KakaoMap;
