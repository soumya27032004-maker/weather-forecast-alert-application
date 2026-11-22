"""Provider adapter can be checked without an internet connection."""
from src import provider


def test_live_adapter_with_mocked_http(monkeypatch):
    calls = []

    def mock_get(url, params=None, timeout=None, headers=None):
        calls.append((url, params))
        class Response:
            def raise_for_status(self):
                pass
            def json(self):
                if "geocoding" in url:
                    return {"results": [{"name": "Test City", "country": "India", "latitude": 10,
                                          "longitude": 20, "timezone": "Asia/Kolkata"}]}
                if "air-quality" in url:
                    return {"current": {"us_aqi": 101}}
                return {
                    "current": {"time": "2026-11-23T10:00", "temperature_2m": 30,
                                "relative_humidity_2m": 70, "apparent_temperature": 33,
                                "precipitation": 0, "wind_speed_10m": 12,
                                "wind_gusts_10m": 20, "weather_code": 2},
                    "hourly": {"time": ["2026-11-23T10:00"], "temperature_2m": [31],
                               "relative_humidity_2m": [71], "precipitation_probability": [65],
                               "precipitation": [0], "wind_speed_10m": [10],
                               "wind_gusts_10m": [30], "uv_index": [4], "weather_code": [3]},
                    "daily": {"time": ["2026-11-23"], "temperature_2m_max": [36],
                              "temperature_2m_min": [24], "precipitation_sum": [2],
                              "precipitation_probability_max": [75],
                              "wind_speed_10m_max": [18], "uv_index_max": [7],
                              "weather_code": [2]}}
        return Response()

    monkeypatch.setattr(provider.requests, "get", mock_get)
    weather = provider.fetch_live_weather("Test City")
    assert weather["source"] == "open-meteo"
    assert weather["current"]["us_aqi"] == 101
    assert weather["hourly"][0]["precipitation_probability_pct"] == 65
    assert weather["daily"][0]["temp_max_c"] == 36
    assert len(calls) == 3
    assert calls[1][1]["wind_speed_unit"] == "kmh"


def test_city_not_found_with_mock(monkeypatch):
    monkeypatch.setattr(provider, "_json_get", lambda _url, _params: {"results": []})
    import pytest
    with pytest.raises(provider.WeatherAPIError, match="was not found"):
        provider.find_location("Nonexistent Land")
