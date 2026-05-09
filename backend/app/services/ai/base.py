# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class AIAnalysisResult:
    name: str
    description: str = ""
    item_type: str = "single"
    brand: str | None = None
    model: str | None = None
    author: str | None = None
    title: str | None = None
    color: str | None = None
    quantity: int = 1
    tags: list[str] = field(default_factory=list)
    confidence: float = 0.0


@runtime_checkable
class AIVisionAdapter(Protocol):
    async def analyze(
        self,
        photo_paths: list[str],
        hint_type: str,
        language: str,
    ) -> AIAnalysisResult:
        ...
