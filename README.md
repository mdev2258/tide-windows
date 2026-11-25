# tidewindow

**When can we actually sail at Emsworth?**

Emsworth's harbour mostly dries, so a nice breeze is useless if there's no water.
`tidewindow` combines the Admiralty tide predictions with an Open-Meteo wind
forecast and tells you when both line up for your boat:

```
Emsworth - topper (5-16 kt, gust <=20), tide >=3.0 m

Sat 28 Nov
  11:50-15:30 (3h40)  11-12 kt, gust 16  SW        tide 3.1>4.5>4.3 m
Sun 29 Nov
  nothing sailable
Mon 30 Nov
  nothing sailable
```

It has no runtime dependencies, only the Python 3.11+ standard library.

## Setup

```bash
pip install -e ".[dev]"
cp config.example.toml config.toml
```

1. Get a free **Discovery** key from the [Admiralty API portal](https://admiraltyapi.portal.azure-api.net)
   (UK Tidal API). Put it in `config.toml` or set `ADMIRALTY_API_KEY` in your environment.
2. Find your tide station: `tidewindow stations emsworth`, then set `station_id`.
3. Set `min_height_m` to the height of tide you actually need to launch and get out.
   **The default of 3.0 m is a guess.** Calibrate it from experience.

## Usage

```bash
tidewindow                       # next 3 days, Toppers
tidewindow -b pico -d 7          # a week, Picos
tidewindow --tides-file tests/fixtures/tides.json \
           --wind-file tests/fixtures/wind.json \
           -c tests/fixtures/config.toml --start 2026-11-28   # offline demo
```

Boat wind limits are in `config.toml`, so add your own classes there.

## How it works

- **Tides:** the free tier only gives high and low water. Heights in between use
  cosine interpolation, a smooth version of the rule of twelfths:
  `h = h0 + (h1 - h0)(1 - cos(pi*f))/2`.
- **Wind:** Open-Meteo hourly speed, gust and direction in knots.
- **Daylight:** sunrise and sunset come from the [sunrise equation](https://en.wikipedia.org/wiki/Sunrise_equation),
  with a margin so you're ashore before dark.
- It walks each day in 10-minute steps. A step is sailable when there's enough water,
  the wind is in range and the gusts are under the limit. Contiguous steps merge into windows.

## Known limitations

- Chichester Harbour tides are asymmetric (a Solent effect), so the cosine model is
  roughest near low water. The paid Admiralty tier has real 30-min heights.
- Wind is a 10 m model forecast, not what you'll feel in the harbour.

## Ideas / roadmap

- [ ] iCal feed of windows (subscribe on your phone)
- [ ] Home Assistant sensor: "can I sail today?"
- [ ] Per-boat minimum depth (keelboats vs dinghies)
- [ ] Wind-direction rules (e.g. strong northerlies = no beginners)
- [ ] Feed slots into a club booking system
