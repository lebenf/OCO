# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl
from typing import List

# Look for .env in the project root (two levels up from this file: app/core/config.py → backend/ → OCO/)
_PROJECT_ROOT = Path(__file__).parents[3]
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/oco.db"

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Admin iniziale
    INITIAL_ADMIN_USERNAME: str = "admin"
    INITIAL_ADMIN_EMAIL: str = "admin@example.com"
    INITIAL_ADMIN_PASSWORD: str = "change-this-password"

    # Storage
    STORAGE_PATH: str = "./data/media"

    # AI
    AI_PROVIDER: str = "ollama"
    AI_TIMEOUT_SECONDS: int = 60

    # Ollama
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llava-llama3"
    OLLAMA_TIMEOUT_SECONDS: int = 300
    OLLAMA_CONCURRENCY: int = 1

    # Claude API
    CLAUDE_API_KEY: str = ""

    # Mistral API
    MISTRAL_API_KEY: str = ""

    # Ports
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3000

    # App
    APP_HOST: str = "http://localhost:3000"
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Uploads
    MAX_UPLOAD_SIZE_MB: int = 20

    # Rate limiting (login endpoint)
    LOGIN_RATE_LIMIT: str = "10/minute"


settings = Settings()
