import json
from datetime import date, timedelta
from pathlib import Path

from tidewindow import config
from tidewindow.cli import main
from tidewindow.tides import parse_admiralty_events
from tidewindow.wind import parse_open_meteo
from tidewindow.windows import find_windows, is_sailable

FX = Path(__file__).parent / "fixtures"
CFG = config.load(FX / "config.toml")
TIDES = parse_admiralty_events(json.loads((FX / "tides.json").read_text()))
WIND = parse_open_meteo(json.loads((FX / "wind.json").read_text()))


def test_saturday_has_a_window_for_toppers():
    ws = find_windows(date(2026, 11, 28), TIDES, WIND, CFG.boats["topper"], CFG.session,
                      CFG.latitude, CFG.longitude)
    assert ws, "expected at least one window on the nice day"
    for w in ws:
        assert w.duration >= CFG.session.min_duration
        assert min(w.heights) >= CFG.session.min_height_m


def test_every_point_in_window_is_sailable():
    boat = CFG.boats["topper"]
    for w in find_windows(date(2026, 11, 28), TIDES, WIND, boat, CFG.session):
        t = w.start
        while t <= w.end:
            assert is_sailable(t, TIDES, WIND, boat, CFG.session)[0]
            t += timedelta(minutes=10)


def test_sunday_too_windy_for_picos():
    assert find_windows(date(2026, 11, 29), TIDES, WIND, CFG.boats["pico"], CFG.session) == []


def test_monday_too_light_for_ilca():
    assert find_windows(date(2026, 11, 30), TIDES, WIND, CFG.boats["ilca6"], CFG.session) == []


def test_cli_offline(capsys):
    rc = main(["-c", str(FX / "config.toml"), "--start", "2026-11-28",
               "--tides-file", str(FX / "tides.json"), "--wind-file", str(FX / "wind.json")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Sat 28 Nov" in out and "kt" in out


def test_daylight_clamp_ends_before_sunset():
    ws = find_windows(date(2026, 11, 28), TIDES, WIND, CFG.boats["topper"], CFG.session,
                      CFG.latitude, CFG.longitude)
    assert ws[-1].end.hour < 16  # sunset ~16:00 GMT in late Nov
