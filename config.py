# config.py
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Максимальные размеры домов в метрах
MAX_BUILDING_SIZES = {
    "house": 20,
    "cottage": 30,
    "warehouse": 60
}

# Теги, запрещающие строительство
FORBIDDEN_TAGS = [
    # (ключ, значение, причина)
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
]

# Теги дорог, по которым можно подъехать
ACCESSIBLE_HIGHWAYS = {
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "unclassified", "residential", "service", "track", "road"
}

MAX_BUILDING_SIZES = {
    "house": 20,      # макс "размер" — для ориентира
    "cottage": 30,
    "warehouse": 60
}