# Configuration Reference

All configuration is done via environment variables in `.env`.

## Database

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/oco.db` | Database connection string. Use `postgresql+asyncpg://user:pass@host/db` for PostgreSQL. |

## Security

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(must change)* | JWT signing key. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh token lifetime in days |

## Initial Admin

Used **only** by `init_db.py` at first run. Ignored afterwards.

| Variable | Default | Description |
|---|---|---|
| `INITIAL_ADMIN_USERNAME` | `admin` | Admin username |
| `INITIAL_ADMIN_EMAIL` | `admin@example.com` | Admin email |
| `INITIAL_ADMIN_PASSWORD` | *(must change)* | Admin password |

## Storage

| Variable | Default | Description |
|---|---|---|
| `STORAGE_PATH` | `./data/media` | Directory for uploaded photos and media files |
| `MAX_UPLOAD_SIZE_MB` | `20` | Maximum upload file size in megabytes |

## AI

| Variable | Default | Description |
|---|---|---|
| `AI_PROVIDER` | `ollama` | Default AI provider: `ollama`, `claude`, or `mistral` |
| `AI_TIMEOUT_SECONDS` | `60` | Maximum time to wait for AI response |

### Ollama

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_URL` | `http://ollama:11434` | Ollama API base URL |
| `OLLAMA_MODEL` | `llava-llama3` | Ollama model name (must support vision) |

### Claude (Anthropic)

| Variable | Default | Description |
|---|---|---|
| `CLAUDE_API_KEY` | *(empty)* | Anthropic API key. Required if `AI_PROVIDER=claude` |

### Mistral

| Variable | Default | Description |
|---|---|---|
| `MISTRAL_API_KEY` | *(empty)* | Mistral API key. Required if `AI_PROVIDER=mistral` |

## Application

| Variable | Default | Description |
|---|---|---|
| `APP_HOST` | `http://localhost:3000` | Public URL of the app. Used for QR code links. |
| `LOG_LEVEL` | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_JSON` | `false` | Set `true` for JSON-formatted logs (recommended in production) |
| `CORS_ORIGINS` | `["http://localhost:3000","http://localhost:5173"]` | Allowed CORS origins (JSON array) |

## Rate Limiting

| Variable | Default | Description |
|---|---|---|
| `LOGIN_RATE_LIMIT` | `10/minute` | Rate limit for the login endpoint per IP. Format: `N/period` (period: `second`, `minute`, `hour`) |

## Runtime AI Config

The admin panel (`/admin/ai-config`) can override `AI_PROVIDER`, `OLLAMA_URL`, `OLLAMA_MODEL`, `CLAUDE_API_KEY`, and `MISTRAL_API_KEY` at runtime without restarting. Changes are persisted in `{STORAGE_PATH}/ai_config.json`.

The runtime config takes precedence over environment variables.
