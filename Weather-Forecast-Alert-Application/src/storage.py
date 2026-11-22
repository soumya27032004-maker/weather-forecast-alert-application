"""SQLite cache and 12-hour alert-notification deduplication."""
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "weather.sqlite"


def _connect(path=DB_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute("""CREATE TABLE IF NOT EXISTS snapshots (
        cache_key TEXT PRIMARY KEY, city TEXT NOT NULL, mode TEXT NOT NULL,
        saved_at TEXT NOT NULL, payload_json TEXT NOT NULL)""")
    connection.execute("""CREATE TABLE IF NOT EXISTS notification_log (
        city TEXT NOT NULL, alert_code TEXT NOT NULL, sent_at TEXT NOT NULL,
        PRIMARY KEY(city, alert_code))""")
    connection.commit()
    return connection


def cache_key(city, mode):
    return f"{mode}:{city.strip().casefold()}"


def save_snapshot(city, mode, payload, path=DB_PATH):
    with _connect(path) as con:
        con.execute("""INSERT INTO snapshots(cache_key, city, mode, saved_at, payload_json)
            VALUES(?,?,?,?,?) ON CONFLICT(cache_key) DO UPDATE SET
            city=excluded.city, mode=excluded.mode, saved_at=excluded.saved_at,
            payload_json=excluded.payload_json""",
            (cache_key(city, mode), city.strip(), mode,
             datetime.now(timezone.utc).isoformat(), json.dumps(payload)))


def load_snapshot(city, mode, max_age_minutes=60, path=DB_PATH):
    with _connect(path) as con:
        row = con.execute("SELECT saved_at,payload_json FROM snapshots WHERE cache_key=?",
                          (cache_key(city, mode),)).fetchone()
    if not row:
        return None
    saved_at, body = row
    if datetime.now(timezone.utc) - datetime.fromisoformat(saved_at) > timedelta(minutes=max_age_minutes):
        return None
    return json.loads(body)


def list_locations(path=DB_PATH):
    with _connect(path) as con:
        rows = con.execute("SELECT city,mode,saved_at FROM snapshots ORDER BY city").fetchall()
    return [{"city": c, "mode": m, "last_updated_utc": updated} for c, m, updated in rows]


def due_for_notification(city, code, cooldown_hours=12, path=DB_PATH):
    with _connect(path) as con:
        row = con.execute("SELECT sent_at FROM notification_log WHERE city=? AND alert_code=?",
                          (city.casefold(), code)).fetchone()
    if row and datetime.now(timezone.utc) - datetime.fromisoformat(row[0]) < timedelta(hours=cooldown_hours):
        return False
    return True


def mark_notification_sent(city, code, path=DB_PATH):
    with _connect(path) as con:
        con.execute("""INSERT INTO notification_log(city,alert_code,sent_at)
                       VALUES(?,?,?) ON CONFLICT(city,alert_code) DO UPDATE SET
                       sent_at=excluded.sent_at""",
                    (city.casefold(), code, datetime.now(timezone.utc).isoformat()))
