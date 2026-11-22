"""Run: python main.py --mode demo --city Delhi"""
import argparse
import sys

from src.alerts import Thresholds
from src.provider import WeatherAPIError
from src.reports import save_all
from src.service import get_weather


def main():
    parser = argparse.ArgumentParser(description="Weather forecast and educational alerts")
    parser.add_argument("--city", default="Delhi", help="City name, e.g., Kolkata")
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    parser.add_argument("--rain", type=int, default=60, help="Rain probability threshold in percent")
    parser.add_argument("--heat", type=float, default=40, help="Heat threshold in Celsius")
    parser.add_argument("--humidity", type=int, default=85)
    parser.add_argument("--wind", type=float, default=54, help="Wind gust threshold in km/h")
    parser.add_argument("--refresh", action="store_true", help="Refetch even if cached")
    parser.add_argument("--no-save", action="store_true", help="Do not export CSV/PNG/report")
    args = parser.parse_args()
    thresholds = Thresholds(rain_probability_pct=args.rain, heat_c=args.heat,
                            humidity_pct=args.humidity, wind_gust_kmh=args.wind)
    try:
        result = get_weather(args.city, args.mode, thresholds, force=args.refresh)
    except (WeatherAPIError, ValueError) as exc:
        print(f"\nERROR: {exc}\nTry offline mode: python main.py --mode demo --city Delhi")
        return 1
    weather = result["weather"]
    current = weather["current"]
    print("\n" + "=" * 57)
    print(f"  WEATHER FORECAST & ALERT APPLICATION — {weather['location']['name']}")
    print("=" * 57)
    print(f"  SOURCE: {'SIMULATION (NOT REAL WEATHER)' if args.mode == 'demo' else 'OPEN-METEO LIVE MODEL'}")
    print(f"  Local observation: {current['time']}")
    print(f"  Temperature: {current['temperature_c']} °C")
    print(f"  Humidity: {current.get('relative_humidity_pct')}%")
    print(f"  Wind speed: {current.get('wind_speed_kmh')} km/h")
    print(f"  US AQI: {current.get('us_aqi') if current.get('us_aqi') is not None else 'Unavailable'}")
    print("\nALERTS:")
    if result["alerts"]:
        for alert in result["alerts"]:
            print(f"  [{alert['severity'].upper()}] {alert['title']}")
            print(f"    {alert['message']}")
    else:
        print("  No custom thresholds were triggered.")
    print("\nNEXT 7 DAYS:")
    for day in weather["daily"][:7]:
        print(f"  {day['date']} | {day['temp_min_c']}–{day['temp_max_c']} °C | Rain {day.get('precipitation_sum_mm')} mm")
    if not args.no_save:
        print("\nSAVED FILES:")
        for label, path in save_all(result).items():
            print(f"  {label}: {path.relative_to(path.parent.parent)}")
    print("\nNOTE: Alerts are educational rules, not official safety warnings.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
