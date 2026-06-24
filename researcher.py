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
from structured_output import StructuredOutputError, extract_json_payload


GEMINI_MODEL = "gemini-2.5-flash"
PROVIDER_GEMINI = "gemini"
PROVIDER_OPENAI = "openai"
PROVIDER_NAMES = {
    PROVIDER_GEMINI: "Gemini",
    PROVIDER_OPENAI: "OpenAI",
}


class ResearcherError(DiagnosticError):
    """Raised when Gemini search cannot produce research output."""


class Researcher:
    """Collect and validate configured-topic research from Gemini."""

    def __init__(
        self,
        prompt_path: str | Path,
        endpoint: str,
        provider: str = PROVIDER_GEMINI,
        model: str = GEMINI_MODEL,
        env_path: str | Path = PROJECT_ENV_PATH,
    ) -> None:
        self.provider = provider
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

        if self.provider == PROVIDER_GEMINI:
            return self._run_gemini(prompt)
        if self.provider == PROVIDER_OPENAI:
            return self._run_openai(prompt)

        raise ResearcherError(f"Unsupported Researcher model provider: {self.provider}")

    def _run_gemini(self, prompt: str) -> dict[str, Any]:
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
            items = extract_json_payload(response_text, list)
        except (KeyError, IndexError, TypeError, StructuredOutputError) as error:
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

        if not items:
            raise ResearcherError(
                "Gemini API search produced no research items",
                {
                    "failure_category": "model_output_empty",
                    "provider_name": "Gemini",
                    "model_name": self.model,
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "raw_model_text_preview": response_text,
                    "provider_search_context_preview": candidate.get("groundingMetadata"),
                },
            )

        return {
            "items": items,
            "grounding_metadata": candidate.get("groundingMetadata"),
        }

    def _run_openai(self, prompt: str) -> dict[str, Any]:
        api_key = load_env_value("OPENAI_API_KEY", self.env_path)

        payload = {
            "model": self.model,
            "input": prompt,
            "tools": [{"type": "web_search"}],
            "tool_choice": "required",
            "include": ["web_search_call.action.sources"],
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        provider_name = PROVIDER_NAMES[PROVIDER_OPENAI]
        try:
            with urllib.request.urlopen(request) as response:
                api_response = json.load(response)
        except urllib.error.URLError as error:
            raise ResearcherError(
                f"{provider_name} API search failed: {error}",
                external_http_context(provider_name, self.model, request, error),
            ) from error
        except json.JSONDecodeError as error:
            raise ResearcherError(
                f"{provider_name} API search failed: {error}",
                {
                    "failure_category": "external_http_call",
                    "provider_name": provider_name,
                    "model_name": self.model,
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "parse_error_message": str(error),
                },
            ) from error

        try:
            response_text = _extract_openai_text(api_response)
            items = extract_json_payload(response_text, list)
        except (KeyError, IndexError, TypeError, StructuredOutputError) as error:
            raise ResearcherError(
                f"Invalid {provider_name} API search response: {error}",
                {
                    "failure_category": "model_output_parse",
                    "provider_name": provider_name,
                    "model_name": self.model,
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "raw_model_text_preview": locals().get("response_text", ""),
                    "parse_error_message": str(error),
                },
            ) from error

        provider_metadata = _extract_openai_metadata(api_response)
        if not items:
            raise ResearcherError(
                f"{provider_name} API search produced no research items",
                {
                    "failure_category": "model_output_empty",
                    "provider_name": provider_name,
                    "model_name": self.model,
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "raw_model_text_preview": response_text,
                    "provider_search_context_preview": provider_metadata,
                },
            )

        return {
            "items": items,
            "grounding_metadata": provider_metadata,
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


def _extract_openai_text(api_response: dict[str, Any]) -> str:
    output_text = api_response.get("output_text")
    if isinstance(output_text, str):
        return output_text

    text_parts: list[str] = []
    for output_item in api_response.get("output", []):
        if output_item.get("type") != "message":
            continue
        for content_item in output_item.get("content", []):
            if isinstance(content_item.get("text"), str):
                text_parts.append(content_item["text"])

    if not text_parts:
        raise KeyError("OpenAI response did not contain output text")
    return "".join(text_parts)


def _extract_openai_metadata(api_response: dict[str, Any]) -> dict[str, Any] | None:
    metadata: dict[str, Any] = {}
    if isinstance(api_response.get("metadata"), dict):
        metadata["metadata"] = api_response["metadata"]
    web_search_calls = [
        item
        for item in api_response.get("output", [])
        if item.get("type") == "web_search_call"
    ]
    if web_search_calls:
        metadata["web_search_calls"] = web_search_calls
    return metadata or None
