#!/usr/bin/env bash
# Letterheads 24/7 live stream: a virtual screen shows letterheads.live/play/?broadcast in Chromium,
# and ffmpeg sends the picture and sound to YouTube Live. Everything restarts itself if it stops.
#
# Settings (environment variables):
#   YT_KEY   your YouTube stream key (required unless OUT is set)
#   URL      page to show            (default https://letterheads.live/play/?broadcast)
#   RES      picture size             (default 1920x1080; use 1280x720 on a small server)
#   FPS      frames per second        (default 30)
#   VBITRATE video bitrate            (default 4500k for 1080p; 2500k suits 720p)
#   OUT      send somewhere else instead of YouTube, e.g. a file (for testing)
#   PROFILE  where the browser keeps the world between restarts (default /data/profile)
set -u
URL="${URL:-https://letterheads.live/play/?broadcast}"
RES="${RES:-1920x1080}"; FPS="${FPS:-30}"; VBITRATE="${VBITRATE:-4500k}"
PROFILE="${PROFILE:-/data/profile}"; CHROME="${CHROME:-chromium}"; FFMPEG="${FFMPEG:-ffmpeg}"
DEST="${OUT:-rtmp://a.rtmp.youtube.com/live2/${YT_KEY:?Set YT_KEY to your YouTube stream key}}"
W="${RES%x*}"; H="${RES#*x}"
export DISPLAY=:99
mkdir -p "$PROFILE"

cleanup(){ kill $(jobs -p) 2>/dev/null; exit 0; }
trap cleanup INT TERM

# 1. A virtual screen.
Xvfb :99 -screen 0 "${W}x${H}x24" -nolisten tcp &
sleep 2

# 2. A virtual sound card, when PulseAudio is installed. Without it the stream carries silence.
AUDIO_IN=(-f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100)
if command -v pulseaudio >/dev/null; then
  pulseaudio --daemonize=yes --exit-idle-time=-1 --system=false 2>/dev/null || true
  sleep 1
  pactl load-module module-null-sink sink_name=stream sink_properties=device.description=stream >/dev/null 2>&1 || true
  pactl set-default-sink stream 2>/dev/null || true
  AUDIO_IN=(-f pulse -i stream.monitor)
fi

# 3. The browser, restarted whenever it exits. The profile keeps the same world alive across restarts.
( while true; do
    "$CHROME" --no-first-run --no-default-browser-check --disable-infobars --kiosk \
      --window-position=0,0 --window-size="${W},${H}" --autoplay-policy=no-user-gesture-required \
      --disable-session-crashed-bubble --disable-features=Translate --user-data-dir="$PROFILE" \
      --no-sandbox --use-gl=angle --use-angle=swiftshader "$URL" >/dev/null 2>&1
    sleep 3
  done ) &
sleep 12

# 4. The encoder, restarted whenever the connection drops.
while true; do
  "$FFMPEG" -hide_banner -loglevel warning \
    -f x11grab -draw_mouse 0 -framerate "$FPS" -video_size "${W}x${H}" -i :99 \
    "${AUDIO_IN[@]}" \
    -c:v libx264 -preset veryfast -tune zerolatency -b:v "$VBITRATE" -maxrate "$VBITRATE" -bufsize 2M \
    -pix_fmt yuv420p -g $((FPS*2)) -keyint_min $((FPS*2)) \
    -c:a aac -b:a 128k -ar 44100 \
    ${OUT:+-t ${DURATION:-20}} -f "${FORMAT:-flv}" "$DEST"
  [ -n "${OUT:-}" ] && break
  echo "Stream stopped; reconnecting in 5 seconds." >&2
  sleep 5
done
cleanup
