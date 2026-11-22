from datetime import datetime
from zoneinfo import ZoneInfo
from src.demo import simulated_weather
from src.reports import save_all
from src.storage import save_snapshot, load_snapshot, list_locations
from api.app import app


def test_simulated_forecast_has_all_expected_hours_and_days():
    w = simulated_weather("Mumbai", now=datetime(2026, 11, 23, tzinfo=ZoneInfo("Asia/Kolkata")))
    assert w["source"] == "simulation"
    assert len(w["hourly"]) == 168
    assert len(w["daily"]) == 7


def test_storage_roundtrip(tmp_path):
    path = tmp_path / "weather.sqlite"
    w = simulated_weather("Delhi")
    save_snapshot("Delhi", "demo", w, path=path)
    assert load_snapshot("Delhi", "demo", path=path)["location"]["name"] == "Delhi"
    assert list_locations(path=path)[0]["city"] == "Delhi"


def test_generate_reports(tmp_path):
    from src.alerts import evaluate_alerts
    w = simulated_weather("Delhi")
    paths = save_all({"weather": w, "alerts": evaluate_alerts(w)}, prefix="sample", root=tmp_path)
    assert all(p.exists() and p.stat().st_size > 100 for p in paths.values())
    assert "SIMULATED DATA" in paths["report"].read_text(encoding="utf-8")


def test_fastapi_endpoints():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    resp = client.get("/weather", params={"city": "Delhi", "mode": "demo"})
    assert resp.status_code == 200
    assert resp.json()["weather"]["source"] == "simulation"
    assert len(client.get("/forecast/daily", params={"city": "Delhi"}).json()["daily"]) == 7
    assert len(client.get("/forecast/hourly", params={"city": "Delhi", "hours": 8}).json()["hourly"]) == 8
    assert client.get("/alerts", params={"city": "Delhi"}).json()["alerts"]
    assert client.get("/weather", params={"city": "X"}).status_code == 422
