"""Gemini search-grounded collector for the Researcher pipeline stage."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from env_config import PROJECT_ENV_PATH, load_env_value
from diagnostics import DiagnosticError, external_http_context
from prompt_loader import PromptLoadError, load_prompt


GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_PROMPT_PATH = Path(__file__).parent / "prompts" / "researchers" / "techno_news.md"


class ResearcherError(DiagnosticError):
    """Raised when Gemini search cannot produce research output."""


class Researcher:
    """Collect and validate recent techno-production research from Gemini."""

    def __init__(
        self,
        model: str = GEMINI_MODEL,
        endpoint: str = GEMINI_ENDPOINT,
        env_path: str | Path = PROJECT_ENV_PATH,
        prompt_path: str | Path = DEFAULT_PROMPT_PATH,
    ) -> None:
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.env_path = Path(env_path)
        self.prompt_path = Path(prompt_path)

    def run(self) -> dict[str, Any]:
        """Search Gemini without Planner input and return items plus grounding data."""
        try:
            prompt = load_prompt(self.prompt_path)
        except PromptLoadError as error:
            raise ResearcherError(str(error)) from error
        api_key = load_env_value("GEMINI_API_KEY", self.env_path)

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "tools": [{"google_search": {}}],
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
            raise ResearcherError(
                f"Gemini API search failed: {error}",
                external_http_context("Gemini", self.model, request, error),
            ) from error
        except json.JSONDecodeError as error:
            raise ResearcherError(
                f"Gemini API search failed: {error}",
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
            items = json.loads(response_text)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise ResearcherError(
                f"Invalid Gemini API search response: {error}",
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

        return {
            "items": items,
            "grounding_metadata": candidate.get("groundingMetadata"),
        }

    @staticmethod
    def validate(output: Any) -> tuple[bool, str]:
        """Validate the item count and required item fields."""
        if not isinstance(output, dict) or not isinstance(output.get("items"), list):
            return False, "Researcher output does not contain an items list"

        items = output["items"]
        if len(items) < 3:
            return False, "Researcher output contains fewer than 3 items"

        required_fields = ("title", "url", "summary")
        for index, item in enumerate(items):
            if not isinstance(item, dict) or any(not item.get(field) for field in required_fields):
                return False, f"Research item {index} is missing a title, url, or summary"

        return True, "At least 3 items contain a title, url, and summary"
