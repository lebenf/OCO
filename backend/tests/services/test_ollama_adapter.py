# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import json

import pytest

from app.services.ai.ollama_adapter import _parse_result


def test_parse_result_valid_object():
    raw = json.dumps({"name": "Lamp", "confidence": 0.9})
    result = _parse_result(raw)
    assert result.name == "Lamp"
    assert result.confidence == 0.9


def test_parse_result_invalid_json_raises_truncated_error():
    raw = "not json at all " + "x" * 1000
    with pytest.raises(ValueError) as exc_info:
        _parse_result(raw)
    assert len(str(exc_info.value)) < 300


def test_parse_result_list_recovers_aggregate_entry():
    raw = json.dumps(
        [
            {"name": "GameCube Controller", "item_type": "single", "confidence": 0.98},
            {"name": "Steering Wheel Controller", "item_type": "single", "confidence": 0.95},
            {"name": "Gaming Controllers Set", "item_type": "set", "confidence": 0.95},
        ]
    )
    result = _parse_result(raw)
    assert result.name == "Gaming Controllers Set"
    assert result.item_type == "set"


def test_parse_result_list_without_aggregate_uses_last_entry():
    raw = json.dumps(
        [
            {"name": "First"},
            {"name": "Last"},
        ]
    )
    result = _parse_result(raw)
    assert result.name == "Last"


def test_parse_result_list_missing_name_raises_truncated_error():
    raw = json.dumps([{"not_name": "x" * 1000}])
    with pytest.raises(ValueError) as exc_info:
        _parse_result(raw)
    assert len(str(exc_info.value)) < 300
