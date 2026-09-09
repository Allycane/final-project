import { useEffect, useRef, useState } from "react";
import "../../styles/KakaoMap.css";

// 마커 개수 30개로 제한
const DEFAULT_MAX_MARKERS = 30;

function KakaoMap({
	center,
	points = [],
	radius,
	maxMarkers = DEFAULT_MAX_MARKERS,
	onCenterChanged,
}) {
	const containerRef = useRef(null);
	const mapRef = useRef(null);
	const markersRef = useRef([]);
	const centerOverlayRef = useRef(null);
	const centerCircleRef = useRef(null);
	const idleListenerRef = useRef(null);
	const [isMapReady, setIsMapReady] = useState(false);
	const onCenterChangedRef = useRef(onCenterChanged);
	useEffect(() => {
		onCenterChangedRef.current = onCenterChanged;
	}, [onCenterChanged]);

	// 지도 생성 + idle 리스너 등록: 마운트 시 딱 한 번만 실행
	useEffect(() => {
		if (!window.kakao || !containerRef.current || mapRef.current) return;

		window.kakao.maps.load(() => {
			if (mapRef.current) return;

			const initialCenter = center ?? { lat: 37.4979, lng: 127.0276 };

			mapRef.current = new window.kakao.maps.Map(containerRef.current, {
				center: new window.kakao.maps.LatLng(
					initialCenter.lat,
					initialCenter.lng,
				),
				level: 5,
			});

			idleListenerRef.current = () => {
				const currentCenter = mapRef.current?.getCenter();
				if (!currentCenter) return;

				onCenterChangedRef.current?.({
					lat: currentCenter.getLat(),
					lng: currentCenter.getLng(),
				});
			};

			window.kakao.maps.event.addListener(
				mapRef.current,
				"idle",
				idleListenerRef.current,
			);

			setIsMapReady(true);
		});

		return () => {
			if (mapRef.current && idleListenerRef.current) {
				window.kakao.maps.event.removeListener(
					mapRef.current,
					"idle",
					idleListenerRef.current,
				);
			}
		};
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	// 2) 서버에서 새 조회 결과가 왔을 때만 지도 중심 옮김
	useEffect(() => {
		if (!isMapReady || !mapRef.current || !center) return;

		mapRef.current.setCenter(
			new window.kakao.maps.LatLng(center.lat, center.lng),
		);
	}, [isMapReady, center]);

	// 3) 업종 분포 마커 그리기 (최대 maxMarkers개까지만 - 가까운 순으로 이미 정렬되어 옴, 앞에서부터 자르면 됨)
	useEffect(() => {
		if (!isMapReady || !mapRef.current) return;

		markersRef.current.forEach((marker) => marker.setMap(null));
		markersRef.current = [];

		points.slice(0, maxMarkers).forEach((point) => {
			const marker = new window.kakao.maps.Marker({
				position: new window.kakao.maps.LatLng(point.lat, point.lng),
				map: mapRef.current,
			});

			markersRef.current.push(marker);

			const infowindow = new window.kakao.maps.InfoWindow({
				content: `<div style="padding:6px 10px;font-size:12px;">${point.name}</div>`,
			});

			window.kakao.maps.event.addListener(marker, "mouseover", () => {
				infowindow.open(mapRef.current, marker);
			});

			window.kakao.maps.event.addListener(marker, "mouseout", () => {
				infowindow.close();
			});
		});
	}, [isMapReady, points, maxMarkers]);

	// 4) 500m 반경의 기준점 (중심 마커 + 반경 원)
	useEffect(() => {
		if (!isMapReady || !mapRef.current) return;

		centerOverlayRef.current?.setMap(null);
		centerOverlayRef.current = null;
		centerCircleRef.current?.setMap(null);
		centerCircleRef.current = null;

		if (!center) return;

		const centerLatLng = new window.kakao.maps.LatLng(center.lat, center.lng);

		const centerContent = document.createElement("div");
		centerContent.className = "kakao-map-center-marker";
		centerContent.title = "조회 기준 중심";

		centerOverlayRef.current = new window.kakao.maps.CustomOverlay({
			position: centerLatLng,
			content: centerContent,
			map: mapRef.current,
			zIndex: 10,
		});

		if (radius) {
			centerCircleRef.current = new window.kakao.maps.Circle({
				center: centerLatLng,
				radius,
				strokeWeight: 2,
				strokeColor: "#237e77",
				strokeOpacity: 0.8,
				strokeStyle: "shortdash",
				fillColor: "#237e77",
				fillOpacity: 0.08,
				map: mapRef.current,
			});
		}
	}, [isMapReady, center, radius]);

	return <div ref={containerRef} className="kakao-map-container" />;
}

export default KakaoMap;
