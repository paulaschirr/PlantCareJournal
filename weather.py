import os
import requests
from functools import lru_cache

API_KEY = os.getenv("OWM_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Set this once – city or lat/lon both work

LOCATION = {
    "lat": 54.245, #Pickering, UK
    "lon": -0.776, #Pickering, UK
    "units": "metric"
}



@lru_cache(maxsize=1)
def get_current_weather():
    """
    Fetch current outdoor temperature and humidity.
    Cached for the session to avoid repeated API calls.
    """
    if not API_KEY:
        return None

    params = {**LOCATION, "appid": API_KEY}

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        return {
            "temp_c": round(data["main"]["temp"], 1),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"]
        }

    except Exception:
        # Fail silently – weather is context, not critical
        return None