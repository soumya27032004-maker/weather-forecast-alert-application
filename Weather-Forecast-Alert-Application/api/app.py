"""FastAPI service. Start with: uvicorn api.app:app --reload"""
from fastapi import FastAPI, HTTPException, Query
from src.provider import WeatherAPIError
from src.service import get_weather
from src.storage import list_locations

app = FastAPI(title="Weather Forecast & Alert API", version="1.0.0",
              description="Open-Meteo model forecasts or clearly labelled simulations. Educational alerts, not official warnings.")


def obtain(city, mode, refresh=False):
    try:
        return get_weather(city, mode, force=refresh)
    except (WeatherAPIError, ValueError) as exc:
        raise HTTPException(status_code=400 if mode == "demo" else 502, detail=str(exc)) from exc


@app.get("/")
def root():
    return {"name": "Weather Forecast & Alert API", "interactive_docs": "/docs", "note": "Not official warnings"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/locations")
def locations():
    return list_locations()


@app.get("/weather")
def weather(city: str = Query("Delhi", min_length=2),
            mode: str = Query("demo", pattern="^(demo|live)$"),
            refresh: bool = False):
    return obtain(city, mode, refresh)


@app.get("/forecast/hourly")
def hourly(city: str = Query("Delhi", min_length=2),
           hours: int = Query(24, ge=1, le=168),
           mode: str = Query("demo", pattern="^(demo|live)$")):
    w = obtain(city, mode)["weather"]
    clock = w["current"]["time"][:16]
    return {"source": w["source"], "city": w["location"]["name"],
            "hourly": [r for r in w["hourly"] if r["time"][:16] >= clock][:hours]}


@app.get("/forecast/daily")
def daily(city: str = Query("Delhi", min_length=2),
          days: int = Query(7, ge=1, le=7),
          mode: str = Query("demo", pattern="^(demo|live)$")):
    w = obtain(city, mode)["weather"]
    return {"source": w["source"], "city": w["location"]["name"],
            "daily": w["daily"][:days]}


@app.get("/alerts")
def alerts(city: str = Query("Delhi", min_length=2),
           mode: str = Query("demo", pattern="^(demo|live)$")):
    r = obtain(city, mode)
    return {"source": r["weather"]["source"], "city": r["weather"]["location"]["name"],
            "alerts": r["alerts"], "disclaimer": "Not official warnings"}
