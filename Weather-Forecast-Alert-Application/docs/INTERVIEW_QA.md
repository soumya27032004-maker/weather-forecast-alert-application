# Weather Forecast & Alert Application — 10 Interview Questions and Answers

### 1. Explain your project.
I built a Python Weather Forecast & Alert Application that retrieves Open-Meteo weather forecasts for a city, processes JSON, evaluates custom weather-risk thresholds, displays charts in Streamlit and APIs in FastAPI, caches live data in SQLite, and exports CSV, JSON, PNG and text reports. I also added an offline simulation and automated tests, so it is easy to demonstrate even without internet.

### 2. What problem does your app solve?
It makes a forecast more actionable. Instead of reading many hourly measurements, a user can see simplified notices about rain, high temperatures, wind, humidity, UV, thunderstorms and optional poor air quality. This can help with personal, travel, event, farming and logistics planning.

### 3. Which technologies did you use and why?
Python is the core language; requests calls HTTP APIs; JSON is the weather data format; pandas structures forecasts and CSV; matplotlib and Streamlit draw charts; FastAPI exposes a separate backend; SQLite caches results; pytest verifies behavior; and dotenv keeps optional notification settings separate from code.

### 4. How do live weather APIs work in this project?
The program sends a city name to a geocoding endpoint to obtain coordinates and a timezone. It then requests forecast fields for that location, receives JSON arrays, and converts them to records. It optionally calls a separate air-quality API for US AQI.

### 5. Why use JSON?
JSON is a standard structured text format for APIs. Open-Meteo returns current weather as named properties and hourly/daily forecast values as parallel arrays; the program aligns timestamps with the matching values.

### 6. How does your alert engine work?
It compares current values or future forecast windows to configurable threshold values. For example, if rain probability reaches 60% in the upcoming 12-hour window, it creates a rain message. Thunderstorm codes also trigger an advisory. These are demonstration rules and are not official disaster warnings.

### 7. How did you prevent incorrect alerts due to timezone/unit mistakes?
The API is requested with the location timezone and km/h wind units. Alerts compare local ISO timestamps, ignore past forecast hours, and use field names that embed units like `_kmh` and `_c`. Missing values are skipped rather than treated as severe weather.

### 8. What happens if the API stops working or the city is invalid?
Requests have a timeout, HTTP errors are caught, malformed responses are rejected, and clear messages are displayed. The application does not silently present simulation as real data; the user can explicitly switch to offline demo mode.

### 9. What outputs and automation did you create?
The dashboard shows weather metrics, a seven-day table, alert notices and interactive charts, and supports downloads. The CLI saves PNG, CSV, JSON and text outputs. An optional foreground monitor can repeatedly check chosen cities and send Telegram notifications with a 12-hour cooldown when configured.

### 10. How would you improve it for a real company?
I would integrate official weather warnings, improve city disambiguation, add deployment and background workers, authenticate users, integrate more weather providers, monitor data freshness, add alert lifecycle/acknowledgment, and set up production observability and secure secrets management.

## HR interview version (30 seconds)
I made a project that helps people understand upcoming weather and possible risks. A user searches for a city, sees an easy dashboard, and receives rule-based messages if rain, extreme heat or strong wind are forecast. I built it in Python using a public API and added offline demo mode, charts, reports and tests. This improved my skills in API integration, data handling, automation and explaining technical work clearly.

## Technical version (45 seconds)
The architecture has Open-Meteo geocoding and forecast ingestion, an adapter that normalizes its JSON, a time-window-aware alert engine, and a SQLite live-data cache. A reusable service feeds both FastAPI routes and a Streamlit dashboard. The report module generates reproducible CSV/PNG/TXT/JSON outputs; a Telegram monitor uses deduplication. I covered alert thresholds, missing fields, caching, API endpoints, and report generation with pytest tests.
