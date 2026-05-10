#!/bin/sh
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
#
# Verifies that .env exists and all required variables are set (non-empty).
# Usage: ./scripts/check-env.sh [path/to/.env]

ENV_FILE="${1:-.env}"

REQUIRED_VARS="
DATABASE_URL
SECRET_KEY
STORAGE_PATH
AI_PROVIDER
APP_HOST
CORS_ORIGINS
BACKEND_PORT
FRONTEND_PORT
ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS
MAX_UPLOAD_SIZE_MB
LOGIN_RATE_LIMIT
"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found. Copy .env.example to .env and configure it." >&2
  exit 1
fi

missing=""
for var in $REQUIRED_VARS; do
  value=$(grep -m1 "^${var}=" "$ENV_FILE" 2>/dev/null | cut -d= -f2-)
  if [ -z "$value" ]; then
    missing="${missing}  - ${var}\n"
  fi
done

if [ -n "$missing" ]; then
  echo "ERROR: missing or empty variables in ${ENV_FILE}:" >&2
  printf "%b" "$missing" >&2
  exit 1
fi

echo "env OK (${ENV_FILE})"
