# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
"""Minimal input sanitization helpers."""

import re

_TAG_RE = re.compile(r"<[^>]+>")
_MAX_TEXT_LEN = 2000
_MAX_NAME_LEN = 255


def strip_html(value: str) -> str:
    return _TAG_RE.sub("", value).strip()


def sanitize_text(value: str, max_len: int = _MAX_TEXT_LEN) -> str:
    return strip_html(value)[:max_len]


def sanitize_name(value: str) -> str:
    return strip_html(value)[:_MAX_NAME_LEN]
