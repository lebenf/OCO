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

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "pixtral-12b-2409"


class MistralAdapter:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.MISTRAL_API_KEY

    async def analyze(self, photo_paths: list[str], hint_type: str, language: str) -> AIAnalysisResult:
        prompt = build_prompt(hint_type, language)
        content: list[dict] = []

        for path in photo_paths:
            full = Path(settings.STORAGE_PATH) / path
            if full.exists():
                b64 = base64.b64encode(full.read_bytes()).decode()
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                })

        content.append({"type": "text", "text": prompt})

        payload = {
            "model": MISTRAL_MODEL,
            "messages": [{"role": "user", "content": content}],
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS + 5) as client:
            resp = await client.post(MISTRAL_API_URL, json=payload, headers=headers)
            resp.raise_for_status()

        raw = resp.json()["choices"][0]["message"]["content"]
        return _parse_result(raw)
