from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from datetime import time, timedelta
from pathlib import Path

from .windows import Boat, Session


@dataclass
class Config:
    location_name: str
    latitude: float
    longitude: float
    station_id: str
    api_key: str
    session: Session
    boats: dict[str, Boat]


def load(path: Path) -> Config:
    raw = tomllib.loads(path.read_text())
    loc, s = raw["location"], raw["session"]
    return Config(
        location_name=loc.get("name", "?"),
        latitude=loc["latitude"],
        longitude=loc["longitude"],
        station_id=loc.get("station_id", ""),
        api_key=os.environ.get("ADMIRALTY_API_KEY") or raw.get("admiralty", {}).get("api_key", ""),
        session=Session(
            start=time.fromisoformat(s["start"]),
            end=time.fromisoformat(s["end"]),
            min_height_m=s["min_height_m"],
            min_duration=timedelta(minutes=s.get("min_duration_min", 60)),
            daylight_only=s.get("daylight_only", True),
            sunset_margin=timedelta(minutes=s.get("sunset_margin_min", 30)),
        ),
        boats={name: Boat(name, **b) for name, b in raw.get("boats", {}).items()},
    )
