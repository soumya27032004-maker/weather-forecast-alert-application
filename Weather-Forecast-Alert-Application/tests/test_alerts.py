from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo
from src.alerts import Thresholds, evaluate_alerts
from src.demo import simulated_weather

FIXED_TIME = datetime(2026, 11, 23, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))


def sample():
    return simulated_weather("Delhi", now=FIXED_TIME)


def test_demo_triggers_all_seven_alert_rules():
    codes = {a["code"] for a in evaluate_alerts(sample())}
    assert codes == {"RAIN", "HEAT", "HUMIDITY", "WIND", "UV", "THUNDERSTORM", "AQI"}


def test_missing_values_are_safe():
    w = sample()
    w["current"]["us_aqi"] = None
    w["current"]["relative_humidity_pct"] = None
    for r in w["hourly"]:
        r["wind_gusts_kmh"] = None
        r["precipitation_probability_pct"] = None
        r["precipitation_mm"] = None
        r["weather_code"] = None
    for d in w["daily"]:
        d["temp_max_c"] = None
        d["uv_index_max"] = None
    assert evaluate_alerts(w) == []


def test_threshold_customization():
    w = sample()
    loose = Thresholds(rain_probability_pct=95, heat_c=49, humidity_pct=99,
                       wind_gust_kmh=95, uv_index=15, us_aqi=300)
    alerts = evaluate_alerts(w, loose)
    assert [a["code"] for a in alerts] == ["RAIN", "THUNDERSTORM"]  # rain also fires for >=2 mm/hour


def test_no_alerts_from_past_hours_only():
    w = sample()
    now = w["current"]["time"]
    for row in w["hourly"]:
        row["time"] = "2026-11-22T00:00"
    for day in w["daily"]:
        day["temp_max_c"] = 30
        day["uv_index_max"] = 2
    w["current"]["relative_humidity_pct"] = 40
    w["current"]["us_aqi"] = 20
    assert not evaluate_alerts(w)
