# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import base64
import json
from pathlib import Path

import httpx

from app.core.config import settings
from app.services.ai.base import AIAnalysisResult
from app.services.ai.prompts import build_prompt


def _coerce_dict(data: object) -> dict | None:
    """Some models answer a 'collection' hint with a list of per-item dicts
    plus an aggregate entry instead of the single flat object the schema
    asks for. Recover the aggregate (or the last dict) rather than failing
    the whole job over a shape mismatch."""
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        dicts = [entry for entry in data if isinstance(entry, dict)]
        for entry in dicts:
            if entry.get("item_type") in ("set", "collection"):
                return entry
        if dicts:
            return dicts[-1]
    return None


def _coerce_scalar(value: object, max_len: int) -> str | None:
    """Vision models sometimes answer a single-value field (color, author, brand...)
    with a list of strings or a list of {"name": ...} objects instead of the plain
    string the schema asks for. Join it into one string rather than failing the
    DB write over a shape mismatch."""
    if value is None:
        return None
    if isinstance(value, list):
        parts = [str(v.get("name", v)) if isinstance(v, dict) else str(v) for v in value if v]
        joined = ", ".join(parts) if parts else None
    else:
        joined = str(value)
    return joined[:max_len] if joined else joined


def _parse_result(raw: str) -> AIAnalysisResult:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI response is not valid JSON: {raw[:200]}") from exc

    obj = _coerce_dict(data)
    if obj is None or "name" not in obj:
        raise ValueError(f"AI response missing required 'name' field: {str(data)[:200]}")

    return AIAnalysisResult(
        name=str(obj.get("name", "")),
        description=str(obj.get("description", "")),
        item_type=str(obj.get("item_type", "single")),
        brand=_coerce_scalar(obj.get("brand"), 100),
        model=_coerce_scalar(obj.get("model"), 100),
        author=_coerce_scalar(obj.get("author"), 255),
        title=_coerce_scalar(obj.get("title"), 500),
        color=_coerce_scalar(obj.get("color"), 100),
        quantity=int(obj.get("quantity", 1)),
        tags=list(obj.get("tags", [])),
        confidence=float(obj.get("confidence", 0.0)),
    )


class OllamaAdapter:
    def __init__(self, url: str | None = None, model: str | None = None) -> None:
        self.url = url or settings.OLLAMA_URL
        self.model = model or settings.OLLAMA_MODEL

    async def analyze(self, photo_paths: list[str], hint_type: str, language: str, name_hint: str | None = None) -> AIAnalysisResult:
        prompt = build_prompt(hint_type, language, name_hint)
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
