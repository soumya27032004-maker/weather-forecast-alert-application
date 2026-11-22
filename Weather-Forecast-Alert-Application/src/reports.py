"""CSV, JSON, text report and matplotlib PNG exports."""
import io
import json
import re
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def dataframe_csv_bytes(records):
    return pd.DataFrame(records).to_csv(index=False).encode("utf-8-sig")


def text_report(weather, alerts):
    c, loc = weather["current"], weather["location"]
    label = "SIMULATED DATA - NOT A REAL FORECAST" if weather["source"] == "simulation" else "MODEL FORECAST - NOT AN OFFICIAL WARNING"
    lines = ["WEATHER FORECAST & ALERT REPORT", label, "=" * 55,
             f"City: {loc['name']} ({loc.get('country','')})",
             f"Provider: {weather['source']}",
             f"Local observation time: {c['time']}",
             f"Last fetched (UTC): {weather['fetched_at']}",
             f"Temperature: {c['temperature_c']} °C",
             f"Humidity: {c.get('relative_humidity_pct')}%",
             f"Wind: {c.get('wind_speed_kmh')} km/h",
             f"US AQI: {c.get('us_aqi') if c.get('us_aqi') is not None else 'Unavailable'}",
             "", "ALERTS"]
    if not alerts:
        lines.append("No custom alert thresholds were triggered.")
    else:
        for a in alerts:
            lines.append(f"[{a['severity'].upper()}] {a['title']}: {a['message']}")
    lines.extend(["", "NEXT SEVEN DAYS"])
    for d in weather["daily"][:7]:
        lines.append(f"{d['date']}: {d.get('temp_min_c')}–{d.get('temp_max_c')} °C, "
                     f"rain {d.get('precipitation_sum_mm')} mm")
    lines.extend(["", "Educational threshold alerts only, not official weather warnings.",
                  "Live provider: Open-Meteo (https://open-meteo.com); air quality model: CAMS via Open-Meteo."])
    return "\n".join(lines) + "\n"


def make_chart(weather, path):
    hourly = weather["hourly"][:24]
    daily = weather["daily"][:7]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10.4, 7), layout="constrained")
    if hourly:
        t = [r["time"][11:16] for r in hourly]
        temps = [r["temperature_c"] for r in hourly]
        ax1.plot(range(len(t)), temps, color="#1779b9", linewidth=2.5, marker=".")
        ax1.set_xticks(range(0, len(t), 3), t[::3]); ax1.set_ylabel("Temperature (°C)")
        ax1.set_title("Next 24 hourly forecast points"); ax1.grid(alpha=0.25)
    if daily:
        dates = [d["date"][5:] for d in daily]
        rain = [d.get("precipitation_sum_mm") or 0 for d in daily]
        ax2.bar(dates, rain, color="#4aa3d8")
        ax2.set_ylabel("Rain (mm)"); ax2.set_title("Seven-day precipitation forecast")
        ax2.grid(axis="y", alpha=0.25)
    tag = "SIMULATION / NOT REAL WEATHER" if weather["source"] == "simulation" else "MODEL FORECAST / NOT AN OFFICIAL ALERT"
    fig.suptitle(f"{weather['location']['name']}  •  {tag}", fontsize=13, fontweight="bold")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def save_all(result, prefix=None, root=ROOT):
    weather, alerts = result["weather"], result["alerts"]
    root = Path(root)
    if prefix is None:
        prefix = re.sub(r"[^a-zA-Z0-9_-]", "_", weather["location"]["name"]) + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "images").mkdir(parents=True, exist_ok=True)
    (root / "outputs").mkdir(parents=True, exist_ok=True)
    paths = {
        "report": root / "reports" / f"{prefix}.txt",
        "hourly_csv": root / "outputs" / f"{prefix}_hourly.csv",
        "daily_csv": root / "outputs" / f"{prefix}_daily.csv",
        "json": root / "outputs" / f"{prefix}.json",
        "chart": root / "images" / f"{prefix}_chart.png",
    }
    paths["report"].write_text(text_report(weather, alerts), encoding="utf-8")
    paths["hourly_csv"].write_bytes(dataframe_csv_bytes(weather["hourly"]))
    paths["daily_csv"].write_bytes(dataframe_csv_bytes(weather["daily"]))
    paths["json"].write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    make_chart(weather, paths["chart"])
    return paths
