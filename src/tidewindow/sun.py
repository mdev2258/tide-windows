"""Sunrise/sunset via the standard sunrise equation (good to a minute or two).

https://en.wikipedia.org/wiki/Sunrise_equation
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone

J2000 = 2451545.0


def _jd_to_dt(jd: float) -> datetime:
    return datetime(2000, 1, 1, 12, tzinfo=timezone.utc) + timedelta(days=jd - J2000)


def sun_times(day: date, lat: float, lon: float) -> tuple[datetime, datetime]:
    """(sunrise, sunset) in UTC. lon is east-positive."""
    n = (datetime(day.year, day.month, day.day, 12) - datetime(2000, 1, 1, 12)).days
    j_star = n - lon / 360
    m = math.radians((357.5291 + 0.98560028 * j_star) % 360)  # mean anomaly
    c = 1.9148 * math.sin(m) + 0.02 * math.sin(2 * m) + 0.0003 * math.sin(3 * m)
    lam = math.radians((math.degrees(m) + c + 180 + 102.9372) % 360)  # ecliptic longitude
    j_transit = J2000 + j_star + 0.0053 * math.sin(m) - 0.0069 * math.sin(2 * lam)
    decl = math.asin(math.sin(lam) * math.sin(math.radians(23.44)))
    phi = math.radians(lat)
    cos_w = (math.sin(math.radians(-0.833)) - math.sin(phi) * math.sin(decl)) / (
        math.cos(phi) * math.cos(decl))
    w = math.degrees(math.acos(max(-1.0, min(1.0, cos_w))))
    return _jd_to_dt(j_transit - w / 360), _jd_to_dt(j_transit + w / 360)
