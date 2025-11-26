# models/geometry.py
from shapely.geometry import Polygon, LineString
from typing import List, Tuple, Dict, Any
from config import FORBIDDEN_OSM_TAGS

def extract_nodes(elements: List[Dict[str, Any]]) -> Dict[int, Tuple[float, float]]:
    return {el['id']: (el['lon'], el['lat']) for el in elements if el['type'] == 'node'}

def build_geometries(elements: List[Dict[str, Any]]) -> Tuple[
    List[Tuple[Polygon, str]],
    List[LineString],
    List[LineString]
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

        # Определяем причину запрета
        obstruction_reason = None
        for key, value, reason in FORBIDDEN_OSM_TAGS:
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
                    # Дороги для подъезда
                    hw = tags.get("highway")
                    if hw and hw in {
                        "motorway", "trunk", "primary", "secondary", "tertiary",
                        "unclassified", "residential", "service", "track", "road"
                    }:
                        roads.append(line)
                    # Линейные запрещённые объекты (реки, ЖД)
                    if obstruction_reason and ("waterway" in tags or "railway" in tags):
                        # Делаем тонкий буфер, чтобы превратить линию в полигон
                        forbidden.append((line.buffer(0.00005), obstruction_reason))
                    if tags.get("bridge") == "yes":
                        bridges.append(line)
        except Exception:
            continue

    # Также обработаем relations (например, protected_area может быть relation)
    for el in elements:
        if el['type'] == 'relation':
            tags = el.get('tags', {})
            # Проверим, является ли relation запрещённой зоной
            for key, value, reason in FORBIDDEN_OSM_TAGS:
                if key in tags and (value is None or tags[key] == value):
                    # В идеале нужно собрать геометрию relation → сложно без библиотеки вроде osm2geojson
                    # Пока пропустим — большинство protected_area есть и как way
                    pass

    return forbidden, roads, bridges