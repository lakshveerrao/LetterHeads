# Letterheads

**The game you can play without playing.** A living world of letters on the real Earth. The Letterheads wake knowing nothing. They find food, make friends, form words, discover fire and walk 300,000 years of human history on their own, from Omo Kibish in Ethiopia to the Palatine Hill in Rome.

Live at **https://letterheads.live** · Play at **https://letterheads.live/play/** · Trailer at **https://letterheads.live/trailer/**

## What is in this repository

| Folder | What it holds |
| --- | --- |
| `site/` | The live website, served as static files. `index.html` is the home page, `play/index.html` is the whole game in one self-contained HTML file, `trailer.mp4` is the 86-second trailer and `trailer/` is its page. `img/` holds the home page's screenshots. |
| `build/atlas/` | Builds the game: `python3 build/atlas/assemble.py` combines `original.html` (the core game), `realworld.js` (real ground, rivers, place names), `atlas.js` (the Atlas of the real Earth) and `trailer_patch.py`, and writes `site/play/index.html`. The `t*.js` and `test*.js` files are Playwright checks. |
| `build/terrain/` | Real elevation for the eleven valley sites (Tilezen terrain tiles), `places.json` with each site's window, place names and vegetation sources. |
| `build/imagery/` | The valley ground: Copernicus Sentinel-2 imagery (`fetch_s2.py`), ESA WorldCover (`fetch_wc.py`), each era's plant cover (`compose.py`), stacked into `ground.jpg` (`stack.py`). Needs `pip install rasterio pyproj mgrs scipy`. |
| `build/film/` | Makes the demo film from the real game: `build_film.py`, `director.js` (every shot as a function of time), `rec.js` (records frames with Playwright), `music.py` (the score), then ffmpeg. |

## Deploying

The site deploys with GitHub Pages: `.github/workflows/pages.yml` publishes the `site` folder on every push to `main`. `site/CNAME` holds the domain, letterheads.live, whose DNS (at Hostinger) points to GitHub Pages.

## Live on YouTube

`letterheads.live/play/?broadcast` shows the world as a clean picture for a 24/7 stream: no buttons, a large caption, a LIVE badge, and the camera always following the best story. `stream/` holds a Docker image that opens that page on a virtual screen and sends it to YouTube Live. See `stream/README.md`. The stream key stays on the server and is never committed.

## Data and credits

Satellite imagery: contains modified Copernicus Sentinel data 2021 to 2023. Land cover: ESA WorldCover 10 m 2021 v200. Elevation: Tilezen terrain tiles on AWS (SRTM, GMTED, ETOPO1 and others). Earth imagery: NASA Blue Marble Next Generation. Sea level after Spratt and Lisiecki (2016) and Lambeck et al. (2014). Per-site vegetation sources are listed in `build/terrain/places.json` and in the game under About the Atlas.

Made by Lakshveer, built with Claude.
