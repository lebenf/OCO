# OCO — moving management web app

**OCO** is a self-hosted moving management web app. Photograph boxes, let AI identify contents, plan transports, and track where everything is.

## Features

- **Box management** — create boxes, scan QR codes, nest boxes inside boxes
- **AI item capture** — photograph an object, AI fills in name/brand/description automatically
- **Multi-provider AI** — Ollama (local, default), Claude API, Mistral API
- **Transfer planning** — FFD bin-packing algorithm groups boxes into vehicle loads
- **Dashboard** — live stats: boxes by status, items, destinations, upcoming transfers
- **Global search** — find any item or box, including via QR scanner
- **PWA** — installable on mobile, works offline for browsing
- **Multi-language** — Italian, English, French, German, Spanish, Portuguese
- **Multi-house** — manage multiple moves simultaneously
- **Admin panel** — user management, AI provider config, house setup

## Quick Start

### Requirements

- Docker or Podman + Compose
- Ollama (optional, for local AI — see [docs/AI_SETUP.md](docs/AI_SETUP.md))

### 1. Clone and configure

```bash
git clone <repo-url> oco
cd oco
cp .env.example .env
# Edit .env — set SECRET_KEY, INITIAL_ADMIN_PASSWORD at minimum
```

### 2. Start

```bash
# With Podman (recommended) — build separata necessaria
make build && make up

# Or with Docker
docker-compose up -d --build
```

### 3. Initialize database

```bash
make init-db
# Creates tables + admin user from INITIAL_ADMIN_* env vars
```

### 4. Open

Navigate to `http://localhost:3000` and log in with your admin credentials.

## Development (no Docker)

Run backend and frontend directly with the local venv.

### Requirements

- Python 3.12+
- Node.js 20+
- `.venv/` already created at project root (see below if missing)

### Setup

```bash
# Create venv if missing
python3 -m venv .venv

# Install backend dependencies
source .venv/bin/activate
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### Configure

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY, INITIAL_ADMIN_PASSWORD at minimum
```

### Run migrations + create admin

```bash
source .venv/bin/activate
cd backend
alembic upgrade head
python -m app.core.init_db
cd ..
```

### Start backend

```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start frontend (separate terminal)

```bash
cd frontend
npm run dev
# Vite dev server on http://localhost:3000
# Proxies /api/* → http://localhost:8000
```

Open `http://localhost:3000` and log in with your admin credentials.

> **Note:** `DATABASE_URL` in `.env` uses a relative path (`./data/oco.db`). When running from `backend/`, the DB is created at `backend/data/oco.db`. Keep both terminals consistent — always `cd backend` before running backend commands.

---

## Documentation

| File | Content |
|---|---|
| [docs/INSTALL.md](docs/INSTALL.md) | Full installation guide |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | All environment variables |
| [docs/AI_SETUP.md](docs/AI_SETUP.md) | AI provider setup (Ollama, Claude, Mistral) |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | Workflow guide |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Local dev setup, running tests |

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy 2 async, Alembic, Pydantic v2 |
| Frontend | Vue 3, Pinia, Vue Router 4, vue-i18n 9, TypeScript |
| Database | SQLite (dev) / PostgreSQL (prod) |
| AI | Ollama (llava-llama3), Claude API, Mistral API |
| Container | Docker / Podman |

## License

MIT
