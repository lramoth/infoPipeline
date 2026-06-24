"""Gemini prompt-based curator for the Curator pipeline stage."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from env_config import PROJECT_ENV_PATH, load_env_value
from diagnostics import DiagnosticError, external_http_context
from prompt_loader import PromptLoadError, load_prompt
from structured_output import StructuredOutputError, extract_json_payload


GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"


class CuratorError(DiagnosticError):
    """Raised when Gemini cannot produce curation output."""


class Curator:
    """Filter and rank researcher items using Gemini."""

    def __init__(
        self,
        prompt_path: str | Path,
        model: str = GEMINI_MODEL,
        endpoint: str = GEMINI_ENDPOINT,
        env_path: str | Path = PROJECT_ENV_PATH,
    ) -> None:
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.env_path = Path(env_path)
        self.prompt_path = Path(prompt_path)

    def run(self, items: list[dict[str, Any]] | dict[str, Any]) -> list[dict[str, Any]]:
        """Curate and rank researcher items via Gemini and return the ranked list."""
        if isinstance(items, dict) and isinstance(items.get("items"), list):
            items = items["items"]

        try:
            prompt_content = load_prompt(self.prompt_path)
        except PromptLoadError as error:
            raise CuratorError(str(error)) from error
        api_key = load_env_value("GEMINI_API_KEY", self.env_path)

        prompt = f"{prompt_content}\n\nResearch items:\n{json.dumps(items, indent=2)}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
        }
        request = urllib.request.Request(
            f"{self.endpoint}/{self.model}:generateContent",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request) as response:
                api_response = json.load(response)
        except urllib.error.URLError as error:
            raise CuratorError(
                f"Gemini API curation failed: {error}",
                external_http_context("Gemini", self.model, request, error),
            ) from error
        except json.JSONDecodeError as error:
            raise CuratorError(
                f"Gemini API curation failed: {error}",
                {
                    "failure_category": "external_http_call",
                    "provider_name": "Gemini",
                    "model_name": self.model,
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "parse_error_message": str(error),
                },
            ) from error

        try:
            candidate = api_response["candidates"][0]
            response_text = "".join(
                part.get("text", "") for part in candidate["content"]["parts"]
            )
            curated_items = extract_json_payload(response_text, list)
        except (KeyError, IndexError, TypeError, StructuredOutputError) as error:
            raise CuratorError(
                f"Invalid Gemini API curation response: {error}",
                {
                    "failure_category": "model_output_parse",
                    "provider_name": "Gemini",
                    "model_name": self.model,
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "raw_model_text_preview": locals().get("response_text", ""),
                    "parse_error_message": str(error),
                },
            ) from error

        return curated_items

    @staticmethod
    def validate(output: Any) -> tuple[bool, str]:
        """Validate item count, required fields, and that rank 1 exists."""
        if not isinstance(output, list):
            return False, "Curator output is not a list"

        if not output:
            return False, "Curator output contains no items"

        required_fields = ("title", "url", "summary", "curation_reason", "rank")
        for index, item in enumerate(output):
            if not isinstance(item, dict) or any(
                item.get(field) is None or item.get(field) == "" for field in required_fields
            ):
                return False, f"Curated item {index} is missing title, url, summary, curation_reason, or rank"

        if not any(item["rank"] == 1 for item in output):
            return False, "No item has rank 1"

        return True, "At least one curated item with all required fields and rank 1"
