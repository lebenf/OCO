.PHONY: up down logs build dev-be dev-fe test-be test-fe test-e2e migrate shell-be init-db backup check-i18n coverage check-env

SHELL := /bin/bash
COMPOSE := podman-compose
VENV := .venv/bin/activate

check-env:
	@./scripts/check-env.sh .env

build:
	podman build -t localhost/oco_backend ./backend
	podman build -t localhost/oco_frontend ./frontend

up: check-env build
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

BACKEND_PORT ?= $(shell grep -m1 '^BACKEND_PORT=' .env 2>/dev/null | cut -d= -f2 || echo 8001)
FRONTEND_PORT ?= $(shell grep -m1 '^FRONTEND_PORT=' .env 2>/dev/null | cut -d= -f2 || echo 3001)

dev-be: check-env
	source $(VENV) && cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT)

dev-fe: check-env
	cd frontend && npm run dev

test-be:
	source $(VENV) && cd backend && pytest -v

test-fe:
	cd frontend && npm run test

test-e2e:
	cd frontend && npm run test:e2e

migrate:
	source $(VENV) && cd backend && alembic upgrade head

shell-be:
	$(COMPOSE) exec backend bash

init-db:
	$(COMPOSE) exec backend python -m app.core.init_db

backup:
	./scripts/backup.sh ./backups

check-i18n:
	cd frontend && npm run check-i18n

coverage:
	source $(VENV) && cd backend && pytest --cov --cov-report=term-missing
