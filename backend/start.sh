#!/bin/sh
# Startup script: create schema, seed, then launch the API server.
# Runs on every deploy — both create_schema and seed are idempotent.

set -e

echo "[start] Creating database schema..."
python create_schema.py

echo "[start] Seeding communities and admin user..."
python seed.py

# Railway injects $PORT; default to 8000 for local/Docker use.
PORT="${PORT:-8000}"
echo "[start] Starting API server on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
