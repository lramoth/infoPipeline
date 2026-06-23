"""Helpers for tolerant structured model-output parsing."""

from __future__ import annotations

import json
import re
from typing import Any


CODE_FENCE_PATTERN = re.compile(r"```(?:[A-Za-z0-9_-]+)?\s*(.*?)\s*```", re.DOTALL)


class StructuredOutputError(ValueError):
    """Raised when model text does not contain a usable structured payload."""


def extract_json_payload(text: str, expected_type: type | tuple[type, ...]) -> Any:
    """Extract the first valid JSON payload matching the expected top-level type."""
    errors: list[str] = []

    for candidate in _candidate_payloads(text):
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError as error:
            errors.append(str(error))
            continue
        if isinstance(payload, expected_type):
            return payload

    decoder = json.JSONDecoder()
    for start_index, character in enumerate(text):
        if character not in "[{":
            continue
        try:
            payload, _ = decoder.raw_decode(text[start_index:])
        except json.JSONDecodeError as error:
            errors.append(str(error))
            continue
        if isinstance(payload, expected_type):
            return payload

    detail = errors[-1] if errors else "no JSON object or array found"
    raise StructuredOutputError(f"No valid structured payload found: {detail}")


def _candidate_payloads(text: str) -> list[str]:
    candidates = [text.strip()]
    candidates.extend(match.group(1).strip() for match in CODE_FENCE_PATTERN.finditer(text))
    return [candidate for candidate in candidates if candidate]
