# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import base64
import json
from pathlib import Path

import httpx

from app.core.config import settings
from app.services.ai.base import AIAnalysisResult
from app.services.ai.prompts import build_prompt
from app.services.ai.ollama_adapter import _parse_result

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-opus-4-7"


class ClaudeAdapter:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.CLAUDE_API_KEY

    async def analyze(self, photo_paths: list[str], hint_type: str, language: str) -> AIAnalysisResult:
        prompt = build_prompt(hint_type, language)
        content: list[dict] = []

        for path in photo_paths:
            full = Path(settings.STORAGE_PATH) / path
            if full.exists():
                b64 = base64.b64encode(full.read_bytes()).decode()
                content.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
                })

        content.append({"type": "text", "text": prompt})

        payload = {
            "model": CLAUDE_MODEL,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": content}],
        }

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS + 5) as client:
            resp = await client.post(CLAUDE_API_URL, json=payload, headers=headers)
            resp.raise_for_status()

        raw = resp.json()["content"][0]["text"]
        return _parse_result(raw)
