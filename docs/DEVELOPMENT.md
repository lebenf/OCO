# Development Guide

## Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- (Optional) Podman or Docker for full-stack dev

### 1. Clone and install

```bash
git clone <repo-url> oco
cd oco

# Python venv (shared for backend)
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 2. Environment

```bash
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY
```

### 3. Database

```bash
source .venv/bin/activate
cd backend
alembic upgrade head
python -m app.core.init_db   # creates admin user
```

### 4. Start dev servers

Terminal 1 — backend:
```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 — frontend:
```bash
cd frontend
npm run dev
# Proxy: /api → http://localhost:8000
```

Open http://localhost:3000

---

## Running Tests

### Backend

```bash
source .venv/bin/activate
cd backend

# All tests
pytest

# With coverage
pytest --cov --cov-report=term-missing

# Specific file
pytest tests/api/test_auth.py -v

# Watch mode (re-run on change)
ptw
```

Coverage target: **> 80%**

### Frontend

```bash
cd frontend

# Unit tests (Vitest)
npm run test

# Watch mode
npm run test:watch

# Type check
npm run type-check

# i18n key check (all locales have same keys)
npm run check-i18n

# E2E (Playwright — requires running app)
npm run test:e2e
```

---

## Project Structure

```
oco/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers (thin layer)
│   │   ├── core/         # Config, DB, deps, security, limiter, sanitize
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic v2 schemas
│   │   └── services/     # Business logic
│   ├── tests/
│   │   ├── api/          # HTTP endpoint tests
│   │   └── services/     # Service unit tests
│   └── alembic/          # DB migrations
├── frontend/
│   └── src/
│       ├── components/   # Reusable Vue components
│       ├── i18n/         # Locales (it, en, fr, de, es, pt)
│       ├── router/       # Vue Router config
│       ├── services/     # Axios API client
│       ├── stores/       # Pinia stores
│       └── views/        # Page-level components
├── scripts/
│   └── backup.sh         # DB + media backup
├── docs/                 # This documentation
├── .env.example
├── docker-compose.yml
├── docker-compose.prod.yml
└── Makefile
```

## Key Conventions

### Backend
- Routers in `app/api/` are thin — delegate to `app/services/`
- FastAPI dependencies (`Depends(...)`) in `app/core/deps.py`
- New migrations: `alembic revision --autogenerate -m "description"` — never edit existing
- All IDs are UUID v4
- API errors: `{"detail": "message", "code": "ERROR_CODE"}`
- Input sanitization via `app/core/sanitize.py` — apply in write schemas

### Frontend
- Composition API with `<script setup>` only
- All API calls go through `src/services/api.ts` (Axios instance with auto-refresh)
- No hardcoded strings in templates — use `$t('key')` always
- `src/views/` = full pages, `src/components/` = reusable pieces

## Adding a New Language

1. Copy `frontend/src/i18n/locales/en.json` to `{locale}.json`
2. Translate all values (keep keys identical)
3. Import and register in `frontend/src/i18n/index.ts`
4. Run `npm run check-i18n` to verify all keys are present

## Adding a Migration

```bash
source .venv/bin/activate
cd backend
alembic revision --autogenerate -m "add_column_X_to_table_Y"
# Review generated file in alembic/versions/
alembic upgrade head
```

Always implement `downgrade()` for reversibility.

## Docker / Podman

```bash
# Build and run everything
make up

# Rebuild after code changes
make build

# View logs
make logs

# Run backend tests in container
make test-be

# Shell into backend container
make shell-be
```
