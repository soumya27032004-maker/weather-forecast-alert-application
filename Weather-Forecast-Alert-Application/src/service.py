"""One entrance for dashboard, CLI, and FastAPI."""
from src.alerts import Thresholds, evaluate_alerts
from src.demo import simulated_weather
from src.provider import fetch_live_weather
from src.storage import load_snapshot, save_snapshot


def get_weather(city="Delhi", mode="demo", thresholds=None, force=False):
    city = city.strip()
    if not city:
        raise ValueError("Please provide a city name.")
    if mode not in {"demo", "live"}:
        raise ValueError("mode must be 'demo' or 'live'")
    # Intentionally never cache demo in order to keep demo timestamps current.
    payload = None if mode == "demo" or force else load_snapshot(city, mode)
    if payload is None:
        payload = simulated_weather(city) if mode == "demo" else fetch_live_weather(city)
        save_snapshot(city, mode, payload)
    return {"weather": payload, "alerts": evaluate_alerts(payload, thresholds or Thresholds())}
