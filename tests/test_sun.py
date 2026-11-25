from datetime import date, timedelta
from zoneinfo import ZoneInfo

from tidewindow.sun import sun_times

LDN = ZoneInfo("Europe/London")
EMS = (50.845, -0.938)


def near(dt, hh, mm, tol=5):
    target = dt.replace(hour=hh, minute=mm, second=0, microsecond=0)
    return abs(dt - target) <= timedelta(minutes=tol)


def test_emsworth_late_november():
    rise, sset = (t.astimezone(LDN) for t in sun_times(date(2026, 11, 25), *EMS))
    assert near(rise, 7, 32) and near(sset, 16, 3)


def test_london_solstices_match_published_times():
    rise, sset = (t.astimezone(LDN) for t in sun_times(date(2026, 6, 21), 51.507, -0.128))
    assert near(rise, 4, 43, 2) and near(sset, 21, 21, 2)
    rise, sset = (t.astimezone(LDN) for t in sun_times(date(2026, 12, 21), 51.507, -0.128))
    assert near(rise, 8, 4, 2) and near(sset, 15, 53, 2)
