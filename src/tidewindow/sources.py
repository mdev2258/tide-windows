"""HTTP fetchers. Stdlib only."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

ADMIRALTY = "https://admiraltyapi.azure-api.net/uktidalapi/api/V1"
OPEN_METEO = "https://api.open-meteo.com/v1/forecast"


def _get(url: str, headers: dict | None = None):
    req = urllib.request.Request(url, headers={"User-Agent": "tidewindow", **(headers or {})})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def admiralty_events(station_id: str, api_key: str, days: int = 7) -> list[dict]:
    return _get(f"{ADMIRALTY}/Stations/{station_id}/TidalEvents?duration={days}",
                {"Ocp-Apim-Subscription-Key": api_key})


def admiralty_stations(api_key: str, name: str | None = None) -> list[dict]:
    q = f"?name={urllib.parse.quote(name)}" if name else ""
    data = _get(f"{ADMIRALTY}/Stations{q}", {"Ocp-Apim-Subscription-Key": api_key})
    return [f["properties"] for f in data.get("features", [])]


def open_meteo_wind(lat: float, lon: float, days: int = 7) -> dict:
    params = urllib.parse.urlencode({
        "latitude": lat, "longitude": lon,
        "hourly": "wind_speed_10m,wind_gusts_10m,wind_direction_10m",
        "wind_speed_unit": "kn", "timezone": "GMT", "forecast_days": days,
    })
    return _get(f"{OPEN_METEO}?{params}")
