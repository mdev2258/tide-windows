from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from . import config as cfg
from . import sources
from .tides import parse_admiralty_events
from .wind import parse_open_meteo
from .windows import LOCAL, Window, find_windows


def fmt_window(w: Window) -> str:
    speeds = [s.speed_kt for s in w.winds]
    gust = max(s.gust_kt for s in w.winds)
    dirs = " ".join(dict.fromkeys(s.compass for s in w.winds))
    mins = int(w.duration.total_seconds() // 60)
    peak = max(w.heights)
    return (f"  {w.start:%H:%M}-{w.end:%H:%M} ({mins // 60}h{mins % 60:02d})  "
            f"{min(speeds):.0f}-{max(speeds):.0f} kt, gust {gust:.0f}  {dirs:<8}  "
            f"tide {w.heights[0]:.1f}>{peak:.1f}>{w.heights[-1]:.1f} m")


def cmd_windows(args, c: cfg.Config) -> int:
    if args.boat not in c.boats:
        print(f"Unknown boat '{args.boat}'. Options: {', '.join(c.boats)}", file=sys.stderr)
        return 2

    if args.tides_file:
        raw_tides = json.loads(Path(args.tides_file).read_text())
    else:
        if not c.api_key or c.station_id in ("", "CHANGE_ME"):
            print("Need an Admiralty API key and station_id in config.toml.", file=sys.stderr)
            return 2
        raw_tides = sources.admiralty_events(c.station_id, c.api_key, args.days)

    raw_wind = (json.loads(Path(args.wind_file).read_text()) if args.wind_file
                else sources.open_meteo_wind(c.latitude, c.longitude, args.days))

    tides, wind = parse_admiralty_events(raw_tides), parse_open_meteo(raw_wind)
    boat = c.boats[args.boat]
    start = (datetime.fromisoformat(args.start).date() if args.start
             else datetime.now(LOCAL).date())

    print(f"{c.location_name} - {boat.name} ({boat.min_wind}-{boat.max_wind} kt, "
          f"gust <={boat.max_gust}), tide >={c.session.min_height_m} m\n")
    for i in range(args.days):
        day = start + timedelta(days=i)
        found = find_windows(day, tides, wind, boat, c.session, c.latitude, c.longitude)
        print(f"{day:%a %d %b}")
        print("\n".join(fmt_window(w) for w in found) if found else "  nothing sailable")
    return 0


def cmd_stations(args, c: cfg.Config) -> int:
    for s in sources.admiralty_stations(c.api_key, args.name):
        print(f"{s['Id']:>8}  {s['Name']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("-c", "--config", default="config.toml")
    p = argparse.ArgumentParser(prog="tidewindow", description="When can we actually sail?")
    sub = p.add_subparsers(dest="cmd")

    w = sub.add_parser("windows", parents=[common], help="list sailable windows (default)")
    w.add_argument("-b", "--boat", default="topper")
    w.add_argument("-d", "--days", type=int, default=3)
    w.add_argument("--start", help="first day, YYYY-MM-DD (default today)")
    w.add_argument("--tides-file", help="use saved Admiralty JSON instead of the API")
    w.add_argument("--wind-file", help="use saved Open-Meteo JSON instead of the API")

    s = sub.add_parser("stations", parents=[common], help="search Admiralty tide stations")
    s.add_argument("name", nargs="?")

    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("windows", "stations", "-h", "--help"):
        argv.insert(0, "windows")
    args = p.parse_args(argv)
    c = cfg.load(Path(args.config))
    return {"windows": cmd_windows, "stations": cmd_stations}[args.cmd](args, c)


if __name__ == "__main__":
    raise SystemExit(main())
