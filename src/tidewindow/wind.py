"""Wind forecast samples from Open-Meteo (hourly, knots, UTC)."""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from datetime import datetime, timezone

COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


@dataclass(frozen=True)
class WindSample:
    time: datetime  # start of the hour, UTC
    speed_kt: float
    gust_kt: float
    direction_deg: float

    @property
    def compass(self) -> str:
        return COMPASS[round(self.direction_deg / 22.5) % 16]


def parse_open_meteo(raw: dict) -> list[WindSample]:
    h = raw["hourly"]
    out = []
    for t, s, g, d in zip(h["time"], h["wind_speed_10m"], h["wind_gusts_10m"], h["wind_direction_10m"]):
        if None in (s, g, d):
            continue
        out.append(WindSample(datetime.fromisoformat(t).replace(tzinfo=timezone.utc), s, g, d))
    return out


def wind_at(t: datetime, samples: list[WindSample]) -> WindSample | None:
    """The hourly sample covering t (no interpolation - forecasts aren't that precise)."""
    i = bisect_right([s.time for s in samples], t) - 1
    if i < 0 or (t - samples[i].time).total_seconds() >= 3600:
        return None
    return samples[i]
