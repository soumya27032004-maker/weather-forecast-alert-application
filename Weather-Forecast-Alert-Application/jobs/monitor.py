"""Run monitor while terminal is open; not a background cloud service."""
import argparse
import time
from src.provider import WeatherAPIError
from src.service import get_weather
from src.notifications import send_telegram_alerts


def run_check(cities, mode, send_demo=False):
    for city in cities:
        try:
            result = get_weather(city, mode=mode, force=True)
            print(f"{city}: {len(result['alerts'])} educational alert(s). Source: {result['weather']['source']}")
            for alert in result["alerts"]:
                print(f"  {alert['severity'].upper()}: {alert['title']}")
            if mode == "live" or send_demo:
                outcome = send_telegram_alerts(city, result["alerts"])
                print(f"  Telegram: {outcome['sent']} sent; {outcome['detail']}")
            else:
                print("  Telegram disabled for simulations (use --send-demo to explicitly test).")
        except WeatherAPIError as exc:
            print(f"{city}: weather API error: {exc}")


def main():
    parser = argparse.ArgumentParser(description="Run hourly live weather checks (window must stay open)")
    parser.add_argument("--cities", nargs="+", default=["Delhi", "Kolkata"])
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    parser.add_argument("--interval-minutes", type=int, default=60)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--send-demo", action="store_true", help="Explicitly allow demo alerts to go to Telegram")
    args = parser.parse_args()
    if not 1 <= args.interval_minutes <= 1440:
        parser.error("--interval-minutes must be 1 to 1440")
    print("Ctrl+C to stop. This monitor runs only while this window stays open.")
    try:
        while True:
            run_check(args.cities, args.mode, args.send_demo)
            if args.once:
                break
            time.sleep(args.interval_minutes * 60)
    except KeyboardInterrupt:
        print("Monitoring stopped.")


if __name__ == "__main__":
    main()
