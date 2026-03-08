#!/bin/sh
set -e
chown -R appuser:appuser /data
exec su appuser -s /bin/sh -c 'uv run uvicorn main:app --host 0.0.0.0 --port "${API_PORT:-54321}"'
