import math
from shapely.geometry import Point, Polygon
from shapely.affinity import rotate
from models.overpass import fetch_osm_data
from models.geometry import build_geometries
from config import MAX_BUILDING_SIZES

def meters_to_degrees_lat(meters: float) -> float:
    return meters / 111132.92

def meters_to_degrees_lon(meters: float, lat: float) -> float:
    lat_rad = math.radians(lat)
    meters_per_deg = 111412.84 * math.cos(lat_rad) - 93.5 * math.cos(3 * lat_rad)
    return meters / meters_per_deg

def create_rotated_house_polygon(lat: float, lon: float, length_m: float, width_m: float, rotation_deg: float) -> Polygon:
    half_l = length_m / 2
    half_w = width_m / 2
    coords_m = [
        (-half_w,  half_l),
        ( half_w,  half_l),
        ( half_w, -half_l),
        (-half_w, -half_l)
    ]
    angle = -rotation_deg
    poly_m = Polygon(coords_m)
    poly_m_rot = rotate(poly_m, angle, origin=(0, 0))
    coords_deg = []
    for x_m, y_m in poly_m_rot.exterior.coords[:-1]:
        d_lat = y_m * meters_to_degrees_lat(1)
        d_lon = x_m * meters_to_degrees_lon(1, lat)
        coords_deg.append((lon + d_lon, lat + d_lat))
    return Polygon(coords_deg)

def is_house_placeable(lat: float, lon: float, length_m: float, width_m: float, rotation_deg: float, building_type: str) -> tuple[bool, str | None]:
    max_size = MAX_BUILDING_SIZES.get(building_type)
    if max_size is None:
        return False, "Неизвестный тип здания"

    if length_m > max_size * 1.8 or width_m > max_size * 1.2:
        return False, f"Размер превышает допустимый для '{building_type}'"

    # Увеличенный радиус поиска (диагональ + 150 м на дороги и зоны)
    diag = math.hypot(length_m, width_m)
    search_radius_deg = meters_to_degrees_lat(diag / 2 + 150)

    data = fetch_osm_data(lat, lon, radius_deg=search_radius_deg)
    elements = data.get("elements", [])

    forbidden_geoms, road_lines, bridge_lines = build_geometries(elements)
    house_poly = create_rotated_house_polygon(lat, lon, length_m, width_m, rotation_deg)

    # 🔴 Проверка 1: пересечение с запрещёнными зонами
    for geom, reason in forbidden_geoms:
        if house_poly.intersects(geom):
            return False, reason  # ✅ Чёткая причина: "Водоём", "Военная зона" и т.д.

    # 🔴 Проверка 2: строительство на мосту
    for bridge in bridge_lines:
        if house_poly.intersects(bridge.buffer(meters_to_degrees_lat(3))):
            return False, "Нельзя строить на мосту"

    # 🟢 Проверка 3: подъезд — есть ЛЮБАЯ проезжая дорога в зоне поиска?
    if not road_lines:
        return False, "Нет подъезда: в районе отсутствуют проезжие дороги"

    # ✅ Если ни одно условие не нарушилось — можно строить
    return True, None