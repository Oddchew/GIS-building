# models.py
from typing import Tuple, Optional

# Примеры "норм": запрещённые зоны (например, охранные, леса, водоёмы)
PROHIBITED_ZONES = [
    {"name": "Forest", "coords": (55.75, 37.62), "radius": 0.02},
    {"name": "River", "coords": (55.76, 37.64), "radius": 0.015},
    {"name": "Protected Area", "coords": (55.74, 37.60), "radius": 0.01}
]

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние в градусах (упрощённо, для примера)"""
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5

def is_allowed_to_build(lat: float, lon: float, building_type: str, size: float) -> Tuple[bool, Optional[str]]:
    """
    Проверяет, можно ли строить на заданной точке.
    size — условный "радиус влияния" здания (в градусах).
    """
    # Пример ограничений по типу здания
    max_sizes = {
        "house": 0.005,
        "cottage": 0.01,
        "warehouse": 0.02
    }

    if building_type not in max_sizes:
        return False, "Неизвестный тип здания"

    if size > max_sizes[building_type]:
        return False, f"Размер превышает максимум для '{building_type}'"

    # Проверка на запрещённые зоны
    for zone in PROHIBITED_ZONES:
        zone_lat, zone_lon = zone["coords"]
        dist = haversine_distance(lat, lon, zone_lat, zone_lon)
        if dist < zone["radius"] + size:
            return False, f"Близко к '{zone['name']}'"

    return True, None