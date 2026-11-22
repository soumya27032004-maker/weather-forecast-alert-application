"""Optional Telegram notifier: only sends if explicitly configured and called."""
import os
import requests
from dotenv import load_dotenv
from src.storage import due_for_notification, mark_notification_sent

load_dotenv()


def send_telegram_alerts(city, alerts):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return {"sent": 0, "detail": "Telegram not configured; alerts remain in dashboard/console."}
    sent = 0
    for alert in alerts:
        if not due_for_notification(city, alert["code"]):
            continue
        msg = (f"⚠️ WeatherWatch: {city}\n{alert['severity'].upper()}: "
               f"{alert['title']}\n{alert['message']}\n"
               "Educational threshold, not an official warning.")
        try:
            response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                                     data={"chat_id": chat_id, "text": msg}, timeout=15)
            response.raise_for_status()
            result = response.json()
            if not result.get("ok"):
                return {"sent": sent, "detail": "Telegram service rejected the message."}
        except (requests.RequestException, ValueError) as exc:
            # Avoid printing token-containing URL from exception to logs.
            return {"sent": sent, "detail": f"Telegram delivery failed ({type(exc).__name__})."}
        mark_notification_sent(city, alert["code"])
        sent += 1
    return {"sent": sent, "detail": "Sent new alerts only (12-hour cooldown per city and rule)."}
