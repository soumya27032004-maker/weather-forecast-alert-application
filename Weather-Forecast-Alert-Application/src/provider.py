"""Open-Meteo geocoding, weather and optional AQI adapter."""
from datetime import datetime, timezone
import requests

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


class WeatherAPIError(RuntimeError):
    """A weather/geocoding service or response failed."""


def _json_get(url, params):
    try:
        response = requests.get(url, params=params, timeout=20,
                                headers={"User-Agent": "student-weather-alert-demo/1.0"})
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise WeatherAPIError(f"Could not contact weather service: {exc}") from exc
    if not isinstance(data, dict) or data.get("error"):
        reason = data.get("reason", "Unexpected API response") if isinstance(data, dict) else "Unexpected response"
        raise WeatherAPIError(f"Weather service rejected the request: {reason}")
    return data


def find_location(city):
    if not isinstance(city, str) or len(city.strip()) < 2:
        raise WeatherAPIError("Please enter a city name with at least 2 characters.")
    result = _json_get(GEO_URL, {"name": city.strip(), "count": 5, "language": "en", "format": "json"})
    places = result.get("results") or []
    if not places:
        raise WeatherAPIError(f"City '{city}' was not found. Try 'Kolkata' or 'Delhi'.")
    # Match the first (highest-ranked) location; avoid claiming all ambiguous names resolve uniquely.
    p = places[0]
    try:
        return {"name": p["name"], "country": p.get("country", ""),
                "latitude": p["latitude"], "longitude": p["longitude"],
                "timezone": p.get("timezone", "auto")}
    except KeyError as exc:
        raise WeatherAPIError(f"Geocoding returned incomplete location data: {exc}") from exc


def _array_records(block, mapping):
    """Build a list of dictionaries from Open-Meteo's parallel JSON arrays."""
    times = block.get("time") or []
    if not isinstance(times, list) or not times:
        raise WeatherAPIError("Weather API returned no forecast timestamps.")
    records = []
    for i, stamp in enumerate(times):
        row = {"time": stamp}
        for local_name, api_name in mapping.items():
            vals = block.get(api_name) or []
            row[local_name] = vals[i] if i < len(vals) else None
        records.append(row)
    return records


def fetch_live_weather(city):
    """Return normalized forecast; AQI is best-effort and may be unavailable."""
    loc = find_location(city)
    lat, lon = loc["latitude"], loc["longitude"]
    raw = _json_get(WEATHER_URL, {
        "latitude": lat, "longitude": lon, "timezone": loc["timezone"],
        "forecast_days": 7, "wind_speed_unit": "kmh",
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,wind_gusts_10m,weather_code",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m,uv_index,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,uv_index_max,weather_code",
    })
    current = raw.get("current") or {}
    if current.get("time") is None or current.get("temperature_2m") is None:
        raise WeatherAPIError("Weather API response is missing current conditions.")
    result = {
        "source": "open-meteo",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "location": loc,
        "current": {
            "time": current.get("time"), "temperature_c": current.get("temperature_2m"),
            "apparent_temperature_c": current.get("apparent_temperature"),
            "relative_humidity_pct": current.get("relative_humidity_2m"),
            "precipitation_mm": current.get("precipitation"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "wind_gusts_kmh": current.get("wind_gusts_10m"),
            "weather_code": current.get("weather_code"), "us_aqi": None,
        },
        "hourly": _array_records(raw.get("hourly") or {}, {
            "temperature_c": "temperature_2m",
            "relative_humidity_pct": "relative_humidity_2m",
            "precipitation_probability_pct": "precipitation_probability",
            "precipitation_mm": "precipitation",
            "wind_speed_kmh": "wind_speed_10m", "wind_gusts_kmh": "wind_gusts_10m",
            "uv_index": "uv_index", "weather_code": "weather_code",
        }),
        "daily": _array_records(raw.get("daily") or {}, {
            "temp_max_c": "temperature_2m_max", "temp_min_c": "temperature_2m_min",
            "precipitation_sum_mm": "precipitation_sum",
            "precipitation_probability_max_pct": "precipitation_probability_max",
            "wind_speed_max_kmh": "wind_speed_10m_max",
            "uv_index_max": "uv_index_max", "weather_code": "weather_code",
        }),
    }
    for record in result["daily"]:
        record["date"] = record.pop("time")
    # A second service may fail; this MUST NOT hide a valid weather forecast.
    try:
        aq = _json_get(AQI_URL, {"latitude": lat, "longitude": lon,
                                "timezone": loc["timezone"], "current": "us_aqi"})
        result["current"]["us_aqi"] = (aq.get("current") or {}).get("us_aqi")
    except WeatherAPIError:
        pass
    return result
