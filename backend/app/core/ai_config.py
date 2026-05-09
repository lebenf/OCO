# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
"""Runtime-mutable AI configuration stored in a JSON file.

Overrides env-var settings without process restart.
"""
import json
from pathlib import Path
from threading import Lock

from app.core.config import settings

_lock = Lock()


def _config_path() -> Path:
    return Path(settings.STORAGE_PATH) / "ai_config.json"


def _load_file() -> dict:
    path = _config_path()
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {}


def get_live_config() -> dict:
    """Merge env defaults with file overrides. Keys: active_provider, ollama_url,
    ollama_model, claude_api_key (empty str if not set), mistral_api_key."""
    defaults = {
        "active_provider": settings.AI_PROVIDER,
        "ollama_url": settings.OLLAMA_URL,
        "ollama_model": settings.OLLAMA_MODEL,
        "claude_api_key": settings.CLAUDE_API_KEY,
        "mistral_api_key": settings.MISTRAL_API_KEY,
    }
    overrides = _load_file()
    return {**defaults, **overrides}


def save_live_config(updates: dict) -> None:
    """Merge updates into current file config and persist."""
    with _lock:
        current = _load_file()
        current.update(updates)
        path = _config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(current, indent=2))
