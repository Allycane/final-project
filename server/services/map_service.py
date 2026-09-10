from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from models.category import MajorCategory, SubCategory

MAX_MARKERS = 30

def _service_codes_for_major(db: Session, major_code: str) -> list[str]:
   rows = (
      db.query(SubCategory.code)
      .join(SubCategory.major)
      .filter(MajorCategory.code == major_code)
      .all()
   )
   return [code for (code,) in rows]


def get_distribution(
   db: Session,
   region: str,
   major_category: str | None,
   sub_categories: list[str],
   radius: int = 500,
   center_lat: float | None = None,
   center_lng: float | None = None,
   marker_limit: int = MAX_MARKERS,
) -> dict:
   service_codes = sub_categories or (
      _service_codes_for_major(db, major_category) if major_category else []
   )
   service_filter_sql = "AND service_code IN :service_codes" if service_codes else ""
   base_params = {"region": region}
   if service_codes:
      base_params["service_codes"] = tuple(service_codes)

   # 마커 개수는 항상 1 ~ MAX_MARKERS 사이로 고정한다.
   marker_limit = max(1, min(marker_limit or MAX_MARKERS, MAX_MARKERS))

   # 1) 중심점 결정
   # 최초 조회: 선택 지역 + 업종에 해당하는 좌표들의 평균 좌표를 사용
   # 이후 지도 조회: 프론트에서 전달한 현재 지도 중심 좌표를 사용한다.
   using_map_center = center_lat is not None and center_lng is not None

   if using_map_center:
      center = {
         "lat": float(center_lat),
         "lng": float(center_lng),
      }
   else:
      center_query = text(
         f"""
         SELECT AVG(longitude) AS lng, AVG(latitude) AS lat
         FROM location
         WHERE district_code = :region
         {service_filter_sql}
         """
      )
      if service_codes:
         center_query = center_query.bindparams(
               bindparam("service_codes", expanding=True)
         )

      center_row = db.execute(center_query, base_params).first()

      if center_row is None or center_row.lat is None or center_row.lng is None:
         return {"center": None, "points": []}

      center = {
         "lat": float(center_row.lat),
         "lng": float(center_row.lng),
      }

   # 2) 그 중심 기준 반경(radius, m) 이내 좌표만 조회
   # 지도를 옮겨서 조회하는 경우(using_map_center=True)에는 자치구를 변경 가능하도록 district_code 조건 X
   district_filter_sql = "" if using_map_center else "AND district_code = :region"
   points_params = {
      "center_lng": center["lng"],
      "center_lat": center["lat"],
      "radius": radius,
      "marker_limit": marker_limit,
   }
   if not using_map_center:
      points_params["region"] = region
   if service_codes:
      points_params["service_codes"] = tuple(service_codes)

   points_query = text(
      f"""
      SELECT
         district_code, service_code, service_name, longitude, latitude,
         ST_Distance_Sphere(
               POINT(longitude, latitude),
               POINT(:center_lng, :center_lat)
         ) AS distance_m
      FROM location
      WHERE 1 = 1
      {district_filter_sql}
      {service_filter_sql}
      HAVING distance_m <= :radius
      ORDER BY distance_m
      LIMIT :marker_limit
      """
   )
   if service_codes:
      points_query = points_query.bindparams(bindparam("service_codes", expanding=True))

   rows = db.execute(points_query, points_params).fetchall()

   points = [
      {
         "id": f"{r.district_code}-{r.service_code}-{i}",
         "name": r.service_name,
         "category": r.service_name,
         "lat": float(r.latitude),
         "lng": float(r.longitude),
      }
      for i, r in enumerate(rows)
   ]

   return {"center": center, "points": points}