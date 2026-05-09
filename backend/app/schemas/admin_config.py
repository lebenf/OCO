# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from pydantic import BaseModel


class OllamaConfigOut(BaseModel):
    url: str
    model: str
    reachable: bool = False


class CloudeConfigOut(BaseModel):
    configured: bool


class MistralConfigOut(BaseModel):
    configured: bool


class AIConfigOut(BaseModel):
    active_provider: str
    ollama: OllamaConfigOut
    claude: CloudeConfigOut
    mistral: MistralConfigOut


class AIConfigUpdate(BaseModel):
    active_provider: str | None = None
    ollama_url: str | None = None
    ollama_model: str | None = None
    claude_api_key: str | None = None
    mistral_api_key: str | None = None


class AITestOut(BaseModel):
    ok: bool
    latency_ms: int | None = None
    provider: str
    error: str | None = None
