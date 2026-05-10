#!/bin/sh
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
set -e

# --- env check ---
REQUIRED="DATABASE_URL SECRET_KEY STORAGE_PATH AI_PROVIDER APP_HOST CORS_ORIGINS BACKEND_PORT FRONTEND_PORT"
missing=""
for var in $REQUIRED; do
  eval "val=\${${var}:-}"
  if [ -z "$val" ]; then
    missing="${missing}  - ${var}\n"
  fi
done
if [ -n "$missing" ]; then
  echo "ERROR: missing or empty environment variables:" >&2
  printf "%b" "$missing" >&2
  exit 1
fi
# --- end env check ---

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${BACKEND_PORT}"
