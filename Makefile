.PHONY: up down logs build test-be test-fe test-e2e migrate shell-be init-db backup check-i18n coverage

SHELL := /bin/bash
COMPOSE := podman-compose
VENV := .venv/bin/activate

build:
	podman build -t localhost/oco_backend ./backend
	podman build -t localhost/oco_frontend ./frontend

up: build
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

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
