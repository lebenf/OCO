# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import time

import httpx
from fastapi import APIRouter, Depends

from app.core.ai_config import get_live_config, save_live_config
from app.core.deps import get_admin_user
from app.models.user import User
from app.schemas.admin_config import AIConfigOut, AIConfigUpdate, AITestOut, OllamaConfigOut, CloudeConfigOut, MistralConfigOut

router = APIRouter()


async def _check_ollama_reachable(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{url}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


@router.get("/config/ai", response_model=AIConfigOut)
async def get_ai_config(_: User = Depends(get_admin_user)):
    cfg = get_live_config()
    reachable = await _check_ollama_reachable(cfg["ollama_url"])
    return AIConfigOut(
        active_provider=cfg["active_provider"],
        ollama=OllamaConfigOut(url=cfg["ollama_url"], model=cfg["ollama_model"], reachable=reachable),
        claude=CloudeConfigOut(configured=bool(cfg.get("claude_api_key"))),
        mistral=MistralConfigOut(configured=bool(cfg.get("mistral_api_key"))),
    )


@router.put("/config/ai", response_model=AIConfigOut)
async def update_ai_config(data: AIConfigUpdate, _: User = Depends(get_admin_user)):
    updates: dict = {}
    if data.active_provider is not None:
        updates["active_provider"] = data.active_provider
    if data.ollama_url is not None:
        updates["ollama_url"] = data.ollama_url
    if data.ollama_model is not None:
        updates["ollama_model"] = data.ollama_model
    if data.claude_api_key is not None:
        updates["claude_api_key"] = data.claude_api_key
    if data.mistral_api_key is not None:
        updates["mistral_api_key"] = data.mistral_api_key

    save_live_config(updates)

    cfg = get_live_config()
    reachable = await _check_ollama_reachable(cfg["ollama_url"])
    return AIConfigOut(
        active_provider=cfg["active_provider"],
        ollama=OllamaConfigOut(url=cfg["ollama_url"], model=cfg["ollama_model"], reachable=reachable),
        claude=CloudeConfigOut(configured=bool(cfg.get("claude_api_key"))),
        mistral=MistralConfigOut(configured=bool(cfg.get("mistral_api_key"))),
    )


@router.post("/config/ai/test", response_model=AITestOut)
async def test_ai_config(_: User = Depends(get_admin_user)):
    cfg = get_live_config()
    provider = cfg["active_provider"]

    if provider == "ollama":
        start = time.monotonic()
        reachable = await _check_ollama_reachable(cfg["ollama_url"])
        latency = int((time.monotonic() - start) * 1000)
        if reachable:
            return AITestOut(ok=True, latency_ms=latency, provider=provider)
        return AITestOut(ok=False, provider=provider, error="Ollama unreachable")

    if provider == "claude":
        if not cfg.get("claude_api_key"):
            return AITestOut(ok=False, provider=provider, error="Claude API key not configured")
        try:
            start = time.monotonic()
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={"x-api-key": cfg["claude_api_key"], "anthropic-version": "2023-06-01"},
                )
                resp.raise_for_status()
            latency = int((time.monotonic() - start) * 1000)
            return AITestOut(ok=True, latency_ms=latency, provider=provider)
        except Exception as exc:
            return AITestOut(ok=False, provider=provider, error=str(exc))

    if provider == "mistral":
        if not cfg.get("mistral_api_key"):
            return AITestOut(ok=False, provider=provider, error="Mistral API key not configured")
        try:
            start = time.monotonic()
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.mistral.ai/v1/models",
                    headers={"Authorization": f"Bearer {cfg['mistral_api_key']}"},
                )
                resp.raise_for_status()
            latency = int((time.monotonic() - start) * 1000)
            return AITestOut(ok=True, latency_ms=latency, provider=provider)
        except Exception as exc:
            return AITestOut(ok=False, provider=provider, error=str(exc))

    return AITestOut(ok=False, provider=provider, error=f"Unknown provider: {provider}")
