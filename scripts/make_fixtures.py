"""Generate fake-but-plausible fixture data for tests and offline demos."""
import json, math
from datetime import datetime, timedelta
from pathlib import Path

out = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
start = datetime(2026, 11, 28, 2, 10)  # a Saturday, UTC
half = timedelta(hours=6, minutes=12)

events = []
for i in range(14):
    high = i % 2 == 0
    events.append({
        "EventType": "HighWater" if high else "LowWater",
        "DateTime": (start + i * half).isoformat(),
        "IsApproximateTime": False,
        "Height": round((4.6 - 0.05 * i) if high else (1.0 + 0.04 * i), 2),
        "IsApproximateHeight": False, "Filtered": False,
    })
(out / "tides.json").write_text(json.dumps(events, indent=1))

times, speed, gust, direction = [], [], [], []
t0 = datetime(2026, 11, 28)
for h in range(72):
    t = t0 + timedelta(hours=h)
    day, hour = divmod(h, 24)
    base = [8, 15, 1][day] + 4 * math.sin(math.pi * (hour - 6) / 12)  # Sat nice, Sun windy, Mon flat
    times.append(t.strftime("%Y-%m-%dT%H:%M"))
    speed.append(round(max(base, 0), 1))
    gust.append(round(max(base, 0) * 1.35, 1))
    direction.append([225, 250, 90][day])
(out / "wind.json").write_text(json.dumps({"hourly": {
    "time": times, "wind_speed_10m": speed,
    "wind_gusts_10m": gust, "wind_direction_10m": direction}}, indent=1))
