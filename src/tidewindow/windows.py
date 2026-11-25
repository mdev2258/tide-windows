"""Combine tide + wind into sailable windows."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from .sun import sun_times
from .tides import TideEvent, height_at
from .wind import WindSample, wind_at

LOCAL = ZoneInfo("Europe/London")
STEP = timedelta(minutes=10)


@dataclass(frozen=True)
class Boat:
    name: str
    min_wind: float
    max_wind: float
    max_gust: float


@dataclass(frozen=True)
class Session:
    start: time
    end: time
    min_height_m: float
    min_duration: timedelta
    daylight_only: bool = True
    sunset_margin: timedelta = timedelta(minutes=30)  # ashore this long before sunset


@dataclass
class Window:
    start: datetime
    end: datetime
    heights: list[float] = field(default_factory=list)
    winds: list[WindSample] = field(default_factory=list)

    @property
    def duration(self) -> timedelta:
        return self.end - self.start


def is_sailable(t: datetime, tides: list[TideEvent], wind: list[WindSample],
                boat: Boat, session: Session) -> tuple[bool, float | None, WindSample | None]:
    h = height_at(t, tides)
    w = wind_at(t, wind)
    ok = (
        h is not None and w is not None
        and h >= session.min_height_m
        and boat.min_wind <= w.speed_kt <= boat.max_wind
        and w.gust_kt <= boat.max_gust
    )
    return ok, h, w


def find_windows(day: date, tides: list[TideEvent], wind: list[WindSample],
                 boat: Boat, session: Session,
                 lat: float | None = None, lon: float | None = None) -> list[Window]:
    t = datetime.combine(day, session.start, LOCAL)
    stop = datetime.combine(day, session.end, LOCAL)
    if session.daylight_only and lat is not None and lon is not None:
        rise, sset = sun_times(day, lat, lon)
        t = max(t, rise.astimezone(LOCAL))
        stop = min(stop, (sset - session.sunset_margin).astimezone(LOCAL))
        t = t.replace(minute=t.minute - t.minute % 10, second=0, microsecond=0) + STEP
    windows: list[Window] = []
    current: Window | None = None

    while t <= stop:
        ok, h, w = is_sailable(t, tides, wind, boat, session)
        if ok:
            if current is None:
                current = Window(t, t)
            current.end = t
            current.heights.append(h)
            if not current.winds or current.winds[-1] is not w:
                current.winds.append(w)
        elif current is not None:
            windows.append(current)
            current = None
        t += STEP
    if current is not None:
        windows.append(current)

    return [w for w in windows if w.duration >= session.min_duration]
