# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_ai_config(auth_client: AsyncClient):
    with patch("app.api.admin.config._check_ollama_reachable", new_callable=AsyncMock, return_value=False):
        resp = await auth_client.get("/api/admin/config/ai")
    assert resp.status_code == 200
    data = resp.json()
    assert "active_provider" in data
    assert "ollama" in data
    assert "claude" in data
    assert "mistral" in data
    assert "api_key" not in str(data)


@pytest.mark.asyncio
async def test_update_ai_config(auth_client: AsyncClient, tmp_path, monkeypatch):
    from app.core import ai_config
    monkeypatch.setattr(ai_config, "_config_path", lambda: tmp_path / "ai_config.json")

    with patch("app.api.admin.config._check_ollama_reachable", new_callable=AsyncMock, return_value=True):
        resp = await auth_client.put(
            "/api/admin/config/ai",
            json={"active_provider": "ollama", "ollama_model": "llava:latest"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ollama"]["model"] == "llava:latest"

    # Verify file was written
    config_file = tmp_path / "ai_config.json"
    assert config_file.exists()
    saved = json.loads(config_file.read_text())
    assert saved["ollama_model"] == "llava:latest"


@pytest.mark.asyncio
async def test_update_does_not_return_api_key(auth_client: AsyncClient, tmp_path, monkeypatch):
    from app.core import ai_config
    monkeypatch.setattr(ai_config, "_config_path", lambda: tmp_path / "ai_config.json")

    with patch("app.api.admin.config._check_ollama_reachable", new_callable=AsyncMock, return_value=False):
        resp = await auth_client.put(
            "/api/admin/config/ai",
            json={"claude_api_key": "sk-secret"},
        )
    assert resp.status_code == 200
    # Key must NOT be in response body
    assert "sk-secret" not in resp.text
    # But configured flag must be true
    assert resp.json()["claude"]["configured"] is True


@pytest.mark.asyncio
async def test_test_ollama_reachable(auth_client: AsyncClient):
    with patch("app.api.admin.config._check_ollama_reachable", new_callable=AsyncMock, return_value=True):
        resp = await auth_client.post("/api/admin/config/ai/test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["provider"] == "ollama"


@pytest.mark.asyncio
async def test_test_ollama_unreachable(auth_client: AsyncClient):
    with patch("app.api.admin.config._check_ollama_reachable", new_callable=AsyncMock, return_value=False):
        resp = await auth_client.post("/api/admin/config/ai/test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is False


@pytest.mark.asyncio
async def test_config_requires_admin(client: AsyncClient):
    resp = await client.get("/api/admin/config/ai")
    assert resp.status_code == 401
