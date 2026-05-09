#!/bin/sh
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
set -e
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
