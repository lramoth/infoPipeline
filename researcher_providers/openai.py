"""OpenAI-backed Researcher provider behavior."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from diagnostics import external_http_context
from env_config import load_env_value
from researcher_providers.errors import ResearcherError
from structured_output import StructuredOutputError, extract_json_payload


class OpenAIResearcherProvider:
    """Run OpenAI web search and parse normalized research items."""

    def __init__(self, model: str, endpoint: str, env_path: str | Path) -> None:
        self.model = model
        self.endpoint = endpoint
        self.env_path = Path(env_path)

    def run(self, prompt: str) -> dict[str, Any]:
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

        try:
            with urllib.request.urlopen(request) as response:
                api_response = json.load(response)
        except urllib.error.URLError as error:
            raise ResearcherError(
                f"OpenAI API search failed: {error}",
                external_http_context("OpenAI", self.model, request, error),
            ) from error
        except json.JSONDecodeError as error:
            raise ResearcherError(
                f"OpenAI API search failed: {error}",
                {
                    "failure_category": "external_http_call",
                    "provider_name": "OpenAI",
                    "model_name": self.model,
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "parse_error_message": str(error),
                },
            ) from error

        try:
            response_text = _extract_text(api_response)
            items = extract_json_payload(response_text, list)
        except (KeyError, IndexError, TypeError, StructuredOutputError) as error:
            response_text = locals().get("response_text", "")
            raise ResearcherError(
                f"Invalid OpenAI API search response: {error}",
                _model_parse_context(
                    self.model,
                    request,
                    response_text,
                    str(error),
                    api_response,
                ),
            ) from error

        provider_metadata = _extract_metadata(api_response)
        if not items:
            raise ResearcherError(
                "OpenAI API search produced no research items",
                {
                    "failure_category": "model_output_empty",
                    "provider_name": "OpenAI",
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


def _extract_text(api_response: dict[str, Any]) -> str:
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


def _extract_metadata(api_response: dict[str, Any]) -> dict[str, Any] | None:
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


def _model_parse_context(
    model_name: str,
    request: urllib.request.Request,
    response_text: str,
    parse_error_message: str,
    provider_response: Any,
) -> dict[str, Any]:
    context: dict[str, Any] = {
        "failure_category": "model_output_parse",
        "provider_name": "OpenAI",
        "model_name": model_name,
        "endpoint_url": request.full_url,
        "http_method": request.get_method(),
        "raw_model_text_preview": response_text,
        "parse_error_message": parse_error_message,
    }
    if not response_text:
        context["provider_response_preview"] = provider_response
    return context
