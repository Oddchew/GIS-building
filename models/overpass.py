# models/overpass.py
import requests
from config import OVERPASS_URL

def fetch_osm_data(lat: float, lon: float, radius_deg: float = 0.02) -> dict:
    s, w, n, e = lat - radius_deg, lon - radius_deg, lat + radius_deg, lon + radius_deg
    query = f"""
    [out:json];
    (
      // Все объекты, которые могут запрещать строительство или обеспечивать подъезд
      way({s},{w},{n},{e});
      relation({s},{w},{n},{e});
      node({s},{w},{n},{e});
    );
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(OVERPASS_URL, data=query, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Overpass error: {e}")
        return {"elements": []}