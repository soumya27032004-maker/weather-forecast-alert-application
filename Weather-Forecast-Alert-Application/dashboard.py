"""Student-friendly Streamlit dashboard. Run: streamlit run dashboard.py"""
import json
import pandas as pd
import streamlit as st
from src.alerts import Thresholds, evaluate_alerts
from src.provider import WeatherAPIError
from src.reports import dataframe_csv_bytes, text_report
from src.service import get_weather

st.set_page_config(page_title="WeatherWatch | Forecast & Alerts", page_icon="⛅", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 2.0rem;}
h1 {letter-spacing:-.04em;}
[data-testid="stMetric"] {padding: 14px 16px; border: 1px solid #d5e1ed; border-radius: 13px;}
</style>
""", unsafe_allow_html=True)
st.title("⛅ WeatherWatch")
st.caption("Weather Forecast & Alert Application · Python + Open-Meteo + Streamlit")

with st.sidebar:
    st.header("⚙️ Settings")
    with st.form("options"):
        city = st.text_input("City", value=st.session_state.get("city", "Delhi"),
                             help="Try Delhi, Mumbai, Kolkata, Bengaluru, or any city in live mode.")
        mode = st.radio("Data source", ["Offline simulation", "Live Open-Meteo"],
                        help="Offline simulation is invented sample data; live requires internet.")
        rain = st.slider("Rain probability alert (%)", 20, 100, 60, step=5)
        heat = st.slider("High temperature alert (°C)", 25, 50, 40)
        humidity = st.slider("Humidity alert (%)", 50, 100, 85, step=5)
        wind = st.slider("Wind gust alert (km/h)", 20, 100, 54, step=2)
        submitted = st.form_submit_button("🔍 Check weather", use_container_width=True, type="primary")
    st.caption("An API key is not required. Live data may be unavailable offline.")

selected_mode = "live" if mode == "Live Open-Meteo" else "demo"
thresholds = Thresholds(rain_probability_pct=rain, heat_c=heat,
                        humidity_pct=humidity, wind_gust_kmh=wind)
if submitted or "result" not in st.session_state:
    try:
        with st.spinner("Loading weather..."):
            st.session_state["result"] = get_weather(city, selected_mode, thresholds, force=submitted)
        st.session_state["city"] = city
        st.session_state["mode"] = selected_mode
    except (WeatherAPIError, ValueError) as exc:
        st.error(f"Unable to get weather: {exc}")
        st.info("You can choose Offline simulation to run the full project without internet.")
        st.stop()

result = st.session_state["result"]
w = result["weather"]
# Sliders can re-evaluate alert rules without refetching the forecast.
alerts = evaluate_alerts(w, thresholds)
if st.session_state.get("mode") != selected_mode:
    st.info("Press **Check weather** to switch the data source.")
if w["source"] == "simulation":
    st.warning("🧪 SIMULATED DEMONSTRATION — All values are invented. These are NOT live weather observations or real warnings.")
else:
    st.info("🌐 Live forecast-model data from Open-Meteo. Alerts below are custom educational thresholds, NOT official warnings.")

st.subheader(f"📍 {w['location']['name']}, {w['location'].get('country', '')}")
st.caption(f"Local observation: {w['current']['time']} · Provider: {w['source']} · Updated (UTC): {w['fetched_at'][:19]}")
c = w["current"]
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Temperature", f"{c.get('temperature_c')} °C")
col2.metric("Feels like", f"{c.get('apparent_temperature_c')} °C")
col3.metric("Humidity", f"{c.get('relative_humidity_pct')}%")
col4.metric("Wind speed", f"{c.get('wind_speed_kmh')} km/h")
col5.metric("US AQI", str(c["us_aqi"]) if c.get("us_aqi") is not None else "N/A")

st.subheader(f"⚠️ Weather alerts ({len(alerts)})")
if not alerts:
    st.success("No custom thresholds were triggered for this forecast.")
for a in alerts:
    message = f"**{a['title']}** — {a['message']}"
    if a["severity"] == "critical":
        st.error(message)
    elif a["severity"] == "warning":
        st.warning(message)
    else:
        st.info(message)

st.subheader("📈 Forecast charts")
left, right = st.columns(2)
h = pd.DataFrame(w["hourly"])
d = pd.DataFrame(w["daily"])
clock = c["time"][:16]
next24 = h.loc[h["time"].str.slice(0, 16) >= clock].head(24).copy()
with left:
    st.caption("Temperature · next 24 hours")
    st.line_chart(next24.set_index("time")[["temperature_c"]], x_label="Local time", y_label="°C")
with right:
    st.caption("Precipitation · next 7 days")
    st.bar_chart(d.set_index("date")[["precipitation_sum_mm"]], x_label="Day", y_label="mm")

st.subheader("🗓️ Daily forecast")
show_cols = ["date", "temp_min_c", "temp_max_c", "precipitation_sum_mm",
             "precipitation_probability_max_pct", "uv_index_max"]
st.dataframe(d[show_cols].rename(columns={
    "date": "Date", "temp_min_c": "Min °C", "temp_max_c": "Max °C",
    "precipitation_sum_mm": "Rain mm", "precipitation_probability_max_pct": "Rain chance %",
    "uv_index_max": "UV Index"}), hide_index=True, use_container_width=True)

lat, lon = w["location"].get("latitude"), w["location"].get("longitude")
if lat is not None and lon is not None:
    st.subheader("🗺️ City location")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=8)

st.subheader("📥 Download project outputs")
a, b, cc, dd = st.columns(4)
a.download_button("Hourly forecast CSV", dataframe_csv_bytes(w["hourly"]),
                  file_name="weather_hourly.csv", mime="text/csv", use_container_width=True)
b.download_button("Daily forecast CSV", dataframe_csv_bytes(w["daily"]),
                  file_name="weather_daily.csv", mime="text/csv", use_container_width=True)
cc.download_button("Text alert report", text_report(w, alerts),
                   file_name="weather_report.txt", mime="text/plain", use_container_width=True)
dd.download_button("JSON result", json.dumps({"weather": w, "alerts": alerts}, indent=2),
                   file_name="weather_data.json", mime="application/json", use_container_width=True)
st.caption("Source: Open-Meteo (https://open-meteo.com). Air-quality data provided by CAMS via Open-Meteo. Forecasts and thresholds can be wrong; follow official advisories for safety decisions.")
