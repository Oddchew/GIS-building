# models/validator.py
import math
from shapely.geometry import Point
from models.overpass import fetch_osm_data
from models.geometry import build_geometries
from config import MAX_BUILDING_SIZES

def meters_to_degrees(meters: float, lat: float) -> float:
    """Конвертирует метры в градусы (с учётом широты)."""
    lat_radians = math.radians(lat)
    meters_per_deg_lat = 111132.92 - 559.82 * math.cos(2 * lat_radians) + 1.175 * math.cos(4 * lat_radians)
    meters_per_deg_lon = 111412.84 * math.cos(lat_radians) - 93.5 * math.cos(3 * lat_radians)
    avg_meters_per_deg = (meters_per_deg_lat + meters_per_deg_lon) / 2
    return meters / avg_meters_per_deg

def is_house_placeable(lat: float, lon: float, size_meters: float, building_type: str) -> tuple[bool, str | None]:
    # Проверка типа и размера
    if building_type not in MAX_BUILDING_SIZES:
        return False, "Неизвестный тип здания"
    if size_meters > MAX_BUILDING_SIZES[building_type]:
        return False, f"Размер превышает максимум для '{building_type}' ({MAX_BUILDING_SIZES[building_type]} м)"

    # Радиус дома в градусах
    radius_deg = meters_to_degrees(size_meters / 2, lat)
    search_radius = radius_deg + meters_to_degrees(50, lat)  # +50 м для дорог

    # Запрос данных
    data = fetch_osm_data(lat, lon, radius_deg=search_radius)
    elements = data.get("elements", [])

    # Построение геометрий
    forbidden_geoms, road_lines, bridge_lines = build_geometries(elements)

    # Дом как круг
    house = Point(lon, lat).buffer(radius_deg)

    # Проверка на пересечение с запрещёнными зонами
    for geom, reason in forbidden_geoms:
        if house.intersects(geom):
            return False, f"Пересечение с: {reason}"

    # Проверка мостов
    for bridge in bridge_lines:
        if house.intersects(bridge.buffer(meters_to_degrees(5, lat))):
            return False, "Нельзя строить на мосту"

    # Проверка подъезда (дорога в пределах 30 м от дома)
    access_dist_deg = meters_to_degrees(30, lat)
    for road in road_lines:
        if house.distance(road) <= access_dist_deg:
            return True, None

    return False, "Нет подъезда: ближайшая проезжая дорога дальше 30 м"