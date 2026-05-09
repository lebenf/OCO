#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
# OCO backup script — backs up SQLite DB and media directory.
# For PostgreSQL, set DATABASE_URL and this script uses pg_dump instead.
# Usage: ./scripts/backup.sh [output_dir]
# Default output_dir: ./backups

set -euo pipefail

OUTPUT_DIR="${1:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="oco_backup_${TIMESTAMP}"
DEST="${OUTPUT_DIR}/${BACKUP_NAME}"

# Load .env if present
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./data/oco.db}"
STORAGE_PATH="${STORAGE_PATH:-./data/media}"

mkdir -p "${DEST}"

echo "[backup] Starting OCO backup → ${DEST}"

# --- Database ---
if [[ "${DATABASE_URL}" == sqlite* ]]; then
  # Extract path from sqlite+aiosqlite:///./data/oco.db
  DB_PATH="${DATABASE_URL#*:///}"
  if [[ -f "${DB_PATH}" ]]; then
    cp "${DB_PATH}" "${DEST}/oco.db"
    echo "[backup] SQLite DB copied: ${DB_PATH}"
  else
    echo "[backup] WARNING: SQLite DB not found at ${DB_PATH}"
  fi
elif [[ "${DATABASE_URL}" == postgresql* ]]; then
  PG_URL="${DATABASE_URL/postgresql+asyncpg/postgresql}"
  pg_dump "${PG_URL}" -F c -f "${DEST}/oco.pgdump"
  echo "[backup] PostgreSQL dump written"
else
  echo "[backup] WARNING: Unknown DATABASE_URL scheme, skipping DB backup"
fi

# --- Media ---
if [[ -d "${STORAGE_PATH}" ]]; then
  tar -czf "${DEST}/media.tar.gz" -C "$(dirname "${STORAGE_PATH}")" "$(basename "${STORAGE_PATH}")"
  echo "[backup] Media archived: ${STORAGE_PATH}"
else
  echo "[backup] WARNING: Media directory not found at ${STORAGE_PATH}"
fi

# --- Compress the whole backup ---
tar -czf "${DEST}.tar.gz" -C "${OUTPUT_DIR}" "${BACKUP_NAME}"
rm -rf "${DEST}"

echo "[backup] Done: ${DEST}.tar.gz"
