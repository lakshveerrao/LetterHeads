FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      chromium xvfb pulseaudio ffmpeg fonts-dejavu-core fonts-noto-color-emoji ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY stream.sh /stream.sh
VOLUME /data
CMD ["/stream.sh"]
