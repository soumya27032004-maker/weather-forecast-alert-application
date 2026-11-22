# 10 development phases and 6-day proof-of-work plan

## Architecture and phase-by-phase implementation

| Phase | What to do (and why) | Expected output | Beginner mistake to avoid |
|---|---|---|---|
| 1. Setup | Install Python; isolate packages in a virtual environment so projects do not conflict. | Working Python and `pip`. | Forgetting "Add Python to PATH". |
| 2. Folders | Split `src`, `api`, `jobs`, `tests`, `outputs`, and `images` so code is organized. | Clean repository structure. | Running commands from the wrong folder. |
| 3. API | Use Open-Meteo's no-key public API; use `.env` **only** for optional Telegram. | No embedded secrets. | Uploading `.env` to GitHub. |
| 4. Fetch | Geocode a city and call forecast endpoint using `requests`. | Weather JSON. | Forgetting internet is needed for live mode. |
| 5. Parse | Transform hourly/daily parallel arrays and normalize units. | Lists of Python dictionaries. | Mixing wind in km/h and m/s. |
| 6. Forecast | Check hours from the current local time; keep daily windows aligned. | Next 12/24 hours and seven-day data. | Reading midnight's past hours as future hours. |
| 7. Alerts | Compare forecasts to configurable thresholds. | Messages for rain, heat, humidity, wind, UV, storms, AQI. | Calling educational thresholds official warnings. |
| 8. Visualize | Use Streamlit and Matplotlib; map city coordinates. | Web dashboard and chart image. | Pretending a simulated chart is live data. |
| 9. Reports | Export CSV, JSON, text report; cache a live result in SQLite. | Repeatable outputs and local storage. | Saving files into the wrong working directory. |
| 10. GitHub | Include README, screenshots, tests, `.gitignore`, and meaningful commits. | Recruiter-friendly repository. | Including environment files, secrets, or unverifiable claims. |

## Your six-day proof building plan

| Day | Goal | Recommended Git commit | Screenshot to capture |
|---|---|---|---|
| 1 | Setup, directory structure, Python and venv. | `chore: create project setup and dependencies` | Extracted folder and terminal showing Python version. |
| 2 | Implement Open-Meteo geocoding and live API integration. | `feat: retrieve Open-Meteo forecasts` | Terminal real source label and weather response (hide sensitive information). |
| 3 | Normalize current, hourly and daily JSON, add SQLite caching. | `feat: parse weather JSON and cache snapshots` | City forecast table and API `/weather` response. |
| 4 | Build threshold rules with tests and offline sample data. | `feat: add seven alert rules and unit tests` | Example alert output **labelled simulated**. |
| 5 | Build dashboard charts and export reports. | `feat: add Streamlit dashboard and CSV reports` | Browser dashboard, forecast chart and CSV. |
| 6 | Polish docs, tests, screenshots, GitHub upload. | `docs: add README, screenshots and demo guide` | Public GitHub repository main page. |

These are a suggested sequence for learning and documenting the work; the distributed project already contains a complete implementation.

## Future production upgrades

1. Use official severe weather advisories for safety-critical alerts.
2. Add scheduled jobs via OS Task Scheduler or APScheduler in a dedicated worker.
3. Add email and SMS notification plugins.
4. Add a proper weather radar tile/map and multiple saved locations.
5. Add authentication and deploy API/UI with monitoring and bounded API request rates.
