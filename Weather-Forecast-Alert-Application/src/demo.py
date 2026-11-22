"""Predictable OFFLINE sample weather; never claim this is a real forecast."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

CITY_COORDS = {
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "kolkata": (22.5726, 88.3639),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "pune": (18.5204, 73.8567),
}


def simulated_weather(city="Delhi", now=None):
    """Create 7 days of invented scenario data to exercise every alert rule."""
    city = city.strip() or "Delhi"
    now = now or datetime.now(ZoneInfo("Asia/Kolkata"))
    # Keeping naive *local* timestamps matches Open-Meteo timezone=auto output.
    start = now.replace(minute=0, second=0, microsecond=0).replace(tzinfo=None)
    lat, lon = CITY_COORDS.get(city.casefold(), (None, None))
    hourly = []
    for i in range(168):
        when = start + timedelta(hours=i)
        hod = when.hour
        rain = i in (3, 4, 5, 6, 7)
        storm = i == 7
        daily_cycle = 5 if 12 <= hod <= 17 else 0
        hourly.append({
            "time": when.isoformat(timespec="minutes"),
            "temperature_c": round(31 + daily_cycle + (i % 3) * 0.3, 1),
            "relative_humidity_pct": 91 if i < 8 else 68,
            "precipitation_probability_pct": 82 if rain else 15,
            "precipitation_mm": 3.2 if rain else 0.0,
            "wind_speed_kmh": 30 if rain else 12,
            "wind_gusts_kmh": 66 if i in (5, 6) else 24,
            "uv_index": 9 if 11 <= hod <= 14 else 1,
            "weather_code": 95 if storm else (61 if rain else 2),
        })
    days = []
    for i in range(7):
        date = (start + timedelta(days=i)).date().isoformat()
        days.append({
            "date": date,
            "temp_max_c": 41 if i in (0, 1) else 34 + (i % 2),
            "temp_min_c": 26 + (i % 2),
            "precipitation_sum_mm": 16 if i == 0 else (5 if i == 1 else 0),
            "precipitation_probability_max_pct": 85 if i == 0 else 30,
            "wind_speed_max_kmh": 34 if i == 0 else 18,
            "uv_index_max": 9 if i == 0 else 6,
            "weather_code": 95 if i == 0 else 2,
        })
    return {
        "source": "simulation",
        "fetched_at": datetime.now(ZoneInfo("UTC")).isoformat(),
        "location": {"name": city, "country": "Demo", "latitude": lat,
                     "longitude": lon, "timezone": "Asia/Kolkata"},
        "current": {"time": start.isoformat(timespec="minutes"),
                    "temperature_c": 35.5, "apparent_temperature_c": 39.1,
                    "relative_humidity_pct": 91, "precipitation_mm": 0,
                    "wind_speed_kmh": 15, "wind_gusts_kmh": 28,
                    "weather_code": 2, "us_aqi": 175},
        "hourly": hourly, "daily": days,
    }
