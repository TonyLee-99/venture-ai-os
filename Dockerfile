# Reproducible offline image: `docker build -t venture-ai-os . && docker run --rm venture-ai-os`
# runs the offline gate (lint, tests, regeneration checks) from committed caches; no keys needed.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends make git && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /usr/local/bin/uv
WORKDIR /app
COPY . .
RUN uv sync --locked
ENV VAIOS_STRICT_REPLAY=1 VAIOS_MAX_CALLS=0
CMD ["make", "check"]
