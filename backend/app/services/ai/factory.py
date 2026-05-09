# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from app.core.ai_config import get_live_config
from app.services.ai.base import AIVisionAdapter


def get_ai_adapter() -> AIVisionAdapter:
    config = get_live_config()
    provider = config["active_provider"].lower()
    if provider == "ollama":
        from app.services.ai.ollama_adapter import OllamaAdapter
        return OllamaAdapter(
            url=config["ollama_url"],
            model=config["ollama_model"],
        )
    if provider == "claude":
        from app.services.ai.claude_adapter import ClaudeAdapter
        return ClaudeAdapter(api_key=config["claude_api_key"])
    if provider == "mistral":
        from app.services.ai.mistral_adapter import MistralAdapter
        return MistralAdapter(api_key=config["mistral_api_key"])
    raise ValueError(f"Unknown AI provider: {provider}")
