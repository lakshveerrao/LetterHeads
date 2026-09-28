# Letterheads Live: the 24/7 YouTube stream

This folder puts the Letterheads valley on YouTube Live, day and night. A small server opens
https://letterheads.live/play/?broadcast in a browser on a virtual screen, and ffmpeg sends the
picture and the game's music to the channel. Broadcast mode hides every button, follows the best
story, shows a large caption, a LIVE badge, the day and the era, and invites viewers to play along.

## 1. Get the stream key (once)
1. In YouTube Studio for the channel, click **Create**, then **Go live**. The first time, YouTube
   may take up to 24 hours to turn live streaming on.
2. Choose **Stream** (not Webcam). Set the title, for example "Letterheads Live: a world of
   letters living through 300,000 years of history", and set **Enable DVR** off and latency to
   **Normal**. Under Stream settings, turn on **Auto-start** and leave **Auto-stop** off.
3. Copy the **stream key**. Keep it secret: anyone with it can stream to the channel.

## 2. Get a server
Any Linux server with **4 CPU cores and 8 GB of memory** runs 1080p smoothly. A 2-core server can
run 720p (`RES=1280x720 VBITRATE=2500k`). Good options cost about 10 to 25 dollars a month,
for example Hetzner CPX31, DigitalOcean 4 GB/2 CPU (720p) or 8 GB/4 CPU (1080p).
Install Docker on it (`curl -fsSL https://get.docker.com | sh`).

## 3. Start the stream
```
git clone https://github.com/lakshveerrao/LetterHeads.git
cd LetterHeads/stream
docker build -t letterheads-live .
docker run -d --name letterheads-live --restart unless-stopped \
  -e YT_KEY=your-stream-key -v letterheads-world:/data letterheads-live
```
Within a minute the stream appears in YouTube Studio and goes live. The `letterheads-world` volume
keeps the same world growing across restarts. `docker logs -f letterheads-live` shows any problems;
`docker rm -f letterheads-live` stops it.

## Settings
`RES` (default 1920x1080), `FPS` (30), `VBITRATE` (4500k), `URL` (the broadcast page). Test
without YouTube: `OUT=/data/test.flv DURATION=30 ./stream.sh` records 30 seconds to a file.
