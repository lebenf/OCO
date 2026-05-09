# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import pytest
from app.services.ai.prompts import build_prompt, HINT_INSTRUCTIONS, SYSTEM_PROMPTS


def test_build_prompt_returns_string():
    prompt = build_prompt("auto", "it")
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_build_prompt_contains_system_and_instruction():
    prompt = build_prompt("single", "it")
    assert SYSTEM_PROMPTS["it"][:20] in prompt
    assert HINT_INSTRUCTIONS["single"]["it"][:20] in prompt


def test_build_prompt_all_hint_types():
    for hint in ("auto", "single", "set", "collection", "book"):
        for lang in ("it", "en"):
            prompt = build_prompt(hint, lang)
            assert len(prompt) > 50


def test_build_prompt_unknown_hint_falls_back_to_auto():
    prompt_auto = build_prompt("auto", "it")
    prompt_unknown = build_prompt("unknown_hint", "it")
    assert prompt_auto == prompt_unknown


def test_build_prompt_unknown_language_falls_back_to_it():
    prompt_it = build_prompt("auto", "it")
    prompt_unknown = build_prompt("auto", "zz")
    assert prompt_it == prompt_unknown


def test_build_prompt_italian_vs_english_differ():
    prompt_it = build_prompt("auto", "it")
    prompt_en = build_prompt("auto", "en")
    assert prompt_it != prompt_en
