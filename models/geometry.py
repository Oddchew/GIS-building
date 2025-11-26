# models/geometry.py
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import polygonize, linemerge
from typing import List, Tuple, Dict, Any

def extract_nodes(elements: List[Dict[str, Any]]) -> Dict[int, Tuple[float, float]]:
    return {el['id']: (el['lon'], el['lat']) for el in elements if el['type'] == 'node'}

def build_geometries(elements: List[Dict[str, Any]]) -> Tuple[
    List[Tuple[Polygon, str]],  # (полигон, причина)
    List[LineString],           # дороги
    List[LineString]            # мосты (bridge=yes)
]:
    nodes = extract_nodes(elements)
    forbidden = []
    roads = []
    bridges = []

    for el in elements:
        if el['type'] != 'way':
            continue
        tags = el.get('tags', {})
        node_ids = el.get('nodes', [])
        coords = [nodes[nid] for nid in node_ids if nid in nodes]
        if len(coords) < 2:
            continue

        # Проверка на запрещённые теги
        obstruction_reason = None
        for key, value, reason in [
            ("building", None, "Здание"),
            ("natural", "water", "Водоём"),
            ("waterway", None, "Река/канал"),
            ("landuse", "forest", "Лес"),
            ("natural", "wood", "Лес"),
            ("landuse", "industrial", "Промышленная зона"),
            ("landuse", "commercial", "Коммерческая зона"),
            ("leisure", "park", "Парк"),
            ("leisure", "garden", "Сад/сквер"),
            ("railway", None, "Железнодорожные пути"),
            ("aeroway", None, "Аэродром"),
            ("military", None, "Военная зона"),
            ("power", "plant", "Электростанция"),
            ("man_made", "works", "Завод"),
        ]:
            if key in tags and (value is None or tags[key] == value):
                obstruction_reason = reason
                break

        is_closed = len(coords) >= 3 and coords[0] == coords[-1]
        try:
            if is_closed:
                poly = Polygon(coords)
                if poly.is_valid and not poly.is_empty:
                    if obstruction_reason:
                        forbidden.append((poly, obstruction_reason))
                    if tags.get("bridge") == "yes":
                        bridges.append(LineString(coords))
            else:
                line = LineString(coords)
                if line.is_valid:
                    # Дороги
                    hw = tags.get("highway")
                    if hw and hw in {
                        "motorway", "trunk", "primary", "secondary", "tertiary",
                        "unclassified", "residential", "service", "track", "road"
                    }:
                        roads.append(line)
                    # Мосты (даже если не дорога)
                    if tags.get("bridge") == "yes":
                        bridges.append(line)
                    # ЖД, реки и т.д. как линии
                    if obstruction_reason and ("railway" in tags or "waterway" in tags):
                        forbidden.append((line.buffer(0.0001), obstruction_reason))  # делаем тонкий буфер
        except Exception:
            continue

    return forbidden, roads, bridges