# Installation Guide

## Prerequisites

- **Podman** >= 4.0 or **Docker** >= 24.0 with Compose plugin
- 2 GB RAM minimum (4 GB recommended if running Ollama locally)
- Port 3000 (frontend) and 8000 (backend) available

## Production Installation

### 1. Clone the repository

```bash
git clone <repo-url> oco
cd oco
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```bash
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
INITIAL_ADMIN_PASSWORD=<strong-password>
INITIAL_ADMIN_EMAIL=admin@yourdomain.com
```

See [CONFIGURATION.md](CONFIGURATION.md) for all options.

### 3. Start services

```bash
# Podman — build esplicita necessaria (podman-compose non supporta --build con short names)
make build
make up

# Docker
docker-compose up -d --build
```

### 4. Initialize database

Run once on first boot to create tables and the admin user:

```bash
make init-db

# Or directly:
# podman-compose exec backend python -m app.core.init_db
```

### 5. Verify

```bash
curl http://localhost:8000/health
# {"status":"ok","db":true,"ai":{"provider":"ollama"}}
```

Open `http://localhost:3000` and log in with your admin credentials.

## PostgreSQL (Production)

Edit `.env`:

```bash
DATABASE_URL=postgresql+asyncpg://oco:password@db:5432/oco
```

Use `docker-compose.prod.yml` which includes a PostgreSQL service:

```bash
podman-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Updating

```bash
git pull
make build
make up
make migrate
```

## Backup

```bash
./scripts/backup.sh ./backups
```

Creates a timestamped `.tar.gz` in `./backups/` containing the database and all media files.

## Data Directory

All persistent data lives in `./data/`:

```
data/
├── oco.db          # SQLite database (dev)
└── media/          # Uploaded photos, QR codes, AI config
```

Mount this as a volume for persistence (already configured in `docker-compose.yml`).

## Firewall / Reverse Proxy

For production, place a reverse proxy (Nginx, Caddy, Traefik) in front:

- Proxy `http://localhost:3000` → your domain
- Enable HTTPS
- Update `APP_HOST` in `.env` to your public URL (used for QR code generation)
- Update `CORS_ORIGINS` to include your domain
