"""Tide events and height interpolation.

The free Admiralty tier only gives high/low water times and heights, so we fill
in the curve between them with cosine interpolation:

    h(t) = h0 + (h1 - h0) * (1 - cos(pi * f)) / 2,   f = (t - t0) / (t1 - t0)

It's a smoothed rule of twelfths. Chichester Harbour's tides are lopsided
(Solent effect), so treat heights near low water as rough.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class TideEvent:
    time: datetime  # tz-aware, UTC
    height_m: float
    is_high: bool


def parse_admiralty_events(raw: list[dict]) -> list[TideEvent]:
    """Parse the Admiralty /TidalEvents response (times are UTC, no suffix)."""
    events = []
    for e in raw:
        if e.get("Height") is None:
            continue
        t = datetime.fromisoformat(e["DateTime"].rstrip("Z"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        events.append(TideEvent(t, float(e["Height"]), e["EventType"] == "HighWater"))
    return sorted(events, key=lambda ev: ev.time)


def height_at(t: datetime, events: list[TideEvent]) -> float | None:
    """Interpolated tide height at t, or None if t is outside the data."""
    for a, b in zip(events, events[1:]):
        if a.time <= t <= b.time:
            f = (t - a.time) / (b.time - a.time)
            return a.height_m + (b.height_m - a.height_m) * (1 - math.cos(math.pi * f)) / 2
    return None
