"""Educational threshold checks, not official meteorological warnings."""
from dataclasses import dataclass

STORM_CODES = {95, 96, 99}


@dataclass(frozen=True)
class Thresholds:
    rain_probability_pct: int = 60
    heat_c: float = 40
    humidity_pct: int = 85
    wind_gust_kmh: float = 54
    uv_index: float = 8
    us_aqi: int = 151


def _numbers(rows, name):
    return [r[name] for r in rows if isinstance(r.get(name), (int, float))]


def evaluate_alerts(data, thresholds=None):
    t = thresholds or Thresholds()
    clock = str(data["current"]["time"])[:16]
    today = clock[:10]
    # Forecasts include midnight-to-now earlier hours. Only evaluate FUTURE windows.
    future = [r for r in data.get("hourly", []) if str(r.get("time", ""))[:16] >= clock]
    next12, next24 = future[:12], future[:24]
    days = [d for d in data.get("daily", []) if d.get("date", "") >= today]
    curr = data.get("current", {})
    found = []

    def add(code, severity, title, message):
        found.append({"code": code, "severity": severity, "title": title, "message": message})

    rain = _numbers(next12, "precipitation_probability_pct")
    rain_mm = _numbers(next12, "precipitation_mm")
    if (rain and max(rain) >= t.rain_probability_pct) or (rain_mm and max(rain_mm) >= 2):
        add("RAIN", "warning", "Rain likely within 12 hours",
            "Carry an umbrella and check the latest local forecast.")

    heat = _numbers(days[:2], "temp_max_c")
    if heat and max(heat) >= t.heat_c:
        add("HEAT", "critical", "High temperature expected",
            f"A daily maximum may reach {max(heat):.1f} °C within two days; take heat precautions.")

    humidity = curr.get("relative_humidity_pct")
    if isinstance(humidity, (int, float)) and humidity >= t.humidity_pct:
        add("HUMIDITY", "info", "High humidity",
            f"Current relative humidity is {humidity}%.")

    gusts = _numbers(next24, "wind_gusts_kmh")
    if gusts and max(gusts) >= t.wind_gust_kmh:
        add("WIND", "warning", "Strong wind gusts possible",
            f"Gusts may reach {max(gusts):.1f} km/h within 24 hours.")

    uv = _numbers(days[:1], "uv_index_max")
    if uv and max(uv) >= t.uv_index:
        add("UV", "warning", "High UV exposure",
            f"Today's modelled UV index may reach {max(uv):.1f}.")

    if any(r.get("weather_code") in STORM_CODES for r in next24):
        add("THUNDERSTORM", "critical", "Thunderstorms possible",
            "A thunderstorm weather code occurs in the next 24-hour forecast.")

    aqi = curr.get("us_aqi")
    if isinstance(aqi, (int, float)) and aqi >= t.us_aqi:
        add("AQI", "warning", "Unhealthy air quality",
            f"Modelled US AQI is {aqi}; consider reducing outdoor exposure.")

    return found
