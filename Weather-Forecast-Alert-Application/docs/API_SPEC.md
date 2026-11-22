# FastAPI quick reference

Start the API with `python -m uvicorn api.app:app --host 127.0.0.1 --port 8000 --reload` while your terminal is in the project root.

Visit http://127.0.0.1:8000/docs to test endpoints from your browser.

| Endpoint | Example | Purpose |
|---|---|---|
| `/health` | `GET /health` | Service heartbeat |
| `/locations` | `GET /locations` | List cached city/mode snapshots |
| `/weather` | `GET /weather?city=Delhi&mode=demo` | Current, 168 hourly entries, 7 daily entries, custom alerts |
| `/weather` | `GET /weather?city=Kolkata&mode=live&refresh=true` | Refresh live weather, requires internet |
| `/forecast/hourly` | `GET /forecast/hourly?city=Delhi&hours=24&mode=demo` | Upcoming hourly records |
| `/forecast/daily` | `GET /forecast/daily?city=Delhi&days=7&mode=demo` | Upcoming daily forecast |
| `/alerts` | `GET /alerts?city=Delhi&mode=demo` | Threshold-triggered messages |

The `mode=demo` responses carry `"source": "simulation"` and **invented values**. Live mode carries `"source": "open-meteo"`. The service is for local development; no user authentication or rate limits are implemented. Do not expose it publicly without suitable production security.

API errors return structured HTTP errors rather than silently replacing live data with demo data. Open-Meteo's geocoder uses the top-ranked result for ambiguous city names.
