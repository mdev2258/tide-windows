from datetime import datetime, timedelta, timezone

from tidewindow.tides import TideEvent, height_at, parse_admiralty_events

UTC = timezone.utc
T0 = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
LW_HW = [TideEvent(T0, 1.0, False), TideEvent(T0 + timedelta(hours=6), 5.0, True)]


def test_endpoints_match_events():
    assert height_at(T0, LW_HW) == 1.0
    assert height_at(T0 + timedelta(hours=6), LW_HW) == 5.0


def test_midpoint_is_half_range():
    assert abs(height_at(T0 + timedelta(hours=3), LW_HW) - 3.0) < 1e-9


def test_roughly_rule_of_twelfths():
    # After 1h the rule of twelfths says 1/12 of the range; cosine gives ~0.067
    h = height_at(T0 + timedelta(hours=1), LW_HW)
    assert 1.2 < h < 1.4


def test_outside_data_is_none():
    assert height_at(T0 - timedelta(minutes=1), LW_HW) is None


def test_parse_sorts_and_skips_missing_heights():
    raw = [
        {"EventType": "HighWater", "DateTime": "2026-01-01T06:00:00", "Height": 5.0},
        {"EventType": "LowWater", "DateTime": "2026-01-01T00:00:00", "Height": 1.0},
        {"EventType": "LowWater", "DateTime": "2026-01-01T12:00:00", "Height": None},
    ]
    ev = parse_admiralty_events(raw)
    assert [e.is_high for e in ev] == [False, True]
    assert ev[0].time.tzinfo is UTC
