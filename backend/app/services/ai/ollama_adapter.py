# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import base64
import json
from pathlib import Path

import httpx

from app.core.config import settings
from app.services.ai.base import AIAnalysisResult
from app.services.ai.prompts import build_prompt


def _parse_result(raw: str) -> AIAnalysisResult:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI response is not valid JSON: {raw[:200]}") from exc
    if not isinstance(data, dict) or "name" not in data:
        raise ValueError(f"AI response missing required 'name' field: {data}")
    return AIAnalysisResult(
        name=str(data.get("name", "")),
        description=str(data.get("description", "")),
        item_type=str(data.get("item_type", "single")),
        brand=data.get("brand"),
        model=data.get("model"),
        author=data.get("author"),
        title=data.get("title"),
        color=data.get("color"),
        quantity=int(data.get("quantity", 1)),
        tags=list(data.get("tags", [])),
        confidence=float(data.get("confidence", 0.0)),
    )


class OllamaAdapter:
    def __init__(self, url: str | None = None, model: str | None = None) -> None:
        self.url = url or settings.OLLAMA_URL
        self.model = model or settings.OLLAMA_MODEL

    async def analyze(self, photo_paths: list[str], hint_type: str, language: str) -> AIAnalysisResult:
        prompt = build_prompt(hint_type, language)
        images = []
        for path in photo_paths:
            full = Path(settings.STORAGE_PATH) / path
            if full.exists():
                images.append(base64.b64encode(full.read_bytes()).decode())

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": images,
            "stream": False,
            "format": "json",
        }

        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS + 5) as client:
            resp = await client.post(f"{self.url}/api/generate", json=payload)
            resp.raise_for_status()

        raw = resp.json().get("response", "")
        return _parse_result(raw)
