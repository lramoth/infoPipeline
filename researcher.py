"""Gemini search-grounded collector for the Researcher pipeline stage."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from env_config import PROJECT_ENV_PATH, load_env_value
from diagnostics import DiagnosticError, bounded_preview, external_http_context, sanitize_url
from prompt_loader import PromptLoadError, load_prompt
from structured_output import StructuredOutputError, extract_json_payload


GEMINI_MODEL = "gemini-2.5-flash"
PROVIDER_GEMINI = "gemini"
PROVIDER_OPENAI = "openai"
PROVIDER_NAMES = {
    PROVIDER_GEMINI: "Gemini",
    PROVIDER_OPENAI: "OpenAI",
}
RAW_PROVIDER_RESPONSE_LIMIT = 12000
SEARCH_CONTEXT_LIMIT = 50


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
            candidate = _extract_gemini_candidate(api_response)
            response_text = _extract_gemini_text(candidate)
        except (KeyError, IndexError, TypeError) as error:
            response_text = locals().get("response_text", "")
            raise ResearcherError(
                f"Invalid Gemini API search response: malformed provider response ({error})",
                _model_parse_context(
                    "Gemini",
                    self.model,
                    request,
                    response_text,
                    str(error),
                    locals().get("candidate", api_response),
                ),
            ) from error

        grounding_metadata = candidate.get("groundingMetadata")
        search_context = _gemini_search_context(grounding_metadata)
        if not _grounding_urls(grounding_metadata):
            raise ResearcherError(
                "Gemini API search produced no usable search source context",
                {
                    "failure_category": "provider_source_context_missing",
                    "provider_name": "Gemini",
                    "model_name": self.model,
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "raw_model_text_preview": response_text,
                    "provider_response_preview": api_response,
                    "provider_search_context_preview": search_context,
                },
            )

        try:
            items = _normalize_gemini_items(response_text, grounding_metadata)
        except StructuredOutputError as error:
            raise ResearcherError(
                f"Gemini API search could not create normalized research items: {error}",
                {
                    "failure_category": "item_normalization_failed",
                    "provider_name": "Gemini",
                    "model_name": self.model,
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "raw_model_text_preview": response_text,
                    "provider_response_preview": api_response,
                    "provider_search_context_preview": search_context,
                    "parse_error_message": str(error),
                },
            ) from error

        return {
            "items": items,
            "grounding_metadata": search_context,
            "raw_provider_response": {
                "provider": "Gemini",
                "model": self.model,
                "response_preview": bounded_preview(
                    api_response,
                    RAW_PROVIDER_RESPONSE_LIMIT,
                ),
                "search_context": search_context,
            },
            "normalization": {
                "source": "gemini_grounded_search",
                "url_source": "provider_grounding_metadata",
            },
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
            response_text = locals().get("response_text", "")
            raise ResearcherError(
                f"Invalid {provider_name} API search response: {error}",
                _model_parse_context(
                    provider_name,
                    self.model,
                    request,
                    response_text,
                    str(error),
                    api_response,
                ),
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


def _extract_gemini_candidate(api_response: dict[str, Any]) -> dict[str, Any]:
    candidate = api_response["candidates"][0]
    if not isinstance(candidate, dict):
        raise TypeError("Gemini candidate is not an object")
    return candidate


def _extract_gemini_text(candidate: dict[str, Any]) -> str:
    parts = candidate["content"]["parts"]
    if not isinstance(parts, list):
        raise TypeError("Gemini content parts is not a list")
    return "".join(part.get("text", "") for part in parts if isinstance(part, dict))


def _normalize_gemini_items(
    response_text: str,
    grounding_metadata: Any,
) -> list[dict[str, str]]:
    seeds = _gemini_item_seeds(response_text)
    if not seeds:
        raise StructuredOutputError("no title and summary items found in provider text")

    urls = _grounding_urls(grounding_metadata)
    if not urls:
        raise StructuredOutputError("no grounded source URLs found")

    normalized_items: list[dict[str, str]] = []
    used_urls: set[str] = set()
    for seed in seeds:
        title = _clean_text(seed.get("title"))
        summary = _clean_text(seed.get("summary"))
        if not title or not summary:
            continue
        url = _grounded_url_for_seed(seed, grounding_metadata, used_urls)
        if not url:
            url = next((candidate for candidate in urls if candidate not in used_urls), "")
        if not url:
            continue
        normalized_items.append({"title": title, "url": url, "summary": summary})
        used_urls.add(url)

    try:
        json.dumps(normalized_items)
    except (TypeError, ValueError) as error:
        raise StructuredOutputError(f"normalized items are not valid JSON: {error}") from error

    if len(normalized_items) < 3:
        raise StructuredOutputError(
            "fewer than 3 normalized items with grounded source URLs were produced"
        )
    return normalized_items


def _gemini_item_seeds(response_text: str) -> list[dict[str, Any]]:
    seeds = _json_item_seeds(response_text)
    if seeds:
        return seeds
    return _line_item_seeds(response_text)


def _json_item_seeds(response_text: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    for start_index, character in enumerate(response_text):
        if character != "[":
            continue
        try:
            payload, end_offset = decoder.raw_decode(response_text[start_index:])
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, list):
            continue
        array_text = response_text[start_index : start_index + end_offset]
        item_spans = _json_array_item_spans(array_text, start_index)
        seeds: list[dict[str, Any]] = []
        for item, span in zip(payload, item_spans):
            if not isinstance(item, dict):
                continue
            title = _clean_text(item.get("title"))
            summary = _clean_text(item.get("summary"))
            if title and summary:
                seeds.append(
                    {
                        "title": title,
                        "summary": summary,
                        "start": span[0],
                        "end": span[1],
                    }
                )
        return seeds
    return []


def _json_array_item_spans(array_text: str, base_index: int) -> list[tuple[int, int]]:
    decoder = json.JSONDecoder()
    spans: list[tuple[int, int]] = []
    index = 1
    while index < len(array_text):
        index = _skip_json_space(array_text, index)
        if index >= len(array_text) or array_text[index] == "]":
            break
        try:
            _, end_offset = decoder.raw_decode(array_text[index:])
        except json.JSONDecodeError:
            break
        spans.append((base_index + index, base_index + index + end_offset))
        index += end_offset
        index = _skip_json_space(array_text, index)
        if index < len(array_text) and array_text[index] == ",":
            index += 1
    return spans


def _skip_json_space(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _line_item_seeds(response_text: str) -> list[dict[str, Any]]:
    seeds: list[dict[str, Any]] = []
    markers = list(_iter_item_markers(response_text))
    if not markers:
        markers = [(0, len(response_text))]
    for marker_index, (start, marker_end) in enumerate(markers):
        end = markers[marker_index + 1][0] if marker_index + 1 < len(markers) else len(response_text)
        block = response_text[marker_end:end]
        title = _field_value(block, "title")
        summary = _field_value(block, "summary")
        if title and summary:
            seeds.append(
                {
                    "title": title,
                    "summary": summary,
                    "start": start,
                    "end": end,
                }
            )
    return seeds


def _iter_item_markers(text: str) -> list[tuple[int, int]]:
    import re

    return [
        (match.start(), match.end())
        for match in re.finditer(r"(?im)^\s*(?:item|result)\s+\d+\s*:?\s*$", text)
    ]


def _field_value(block: str, field_name: str) -> str:
    import re

    pattern = re.compile(
        rf"(?ims)^\s*{re.escape(field_name)}\s*:\s*(.+?)(?=^\s*(?:title|summary)\s*:|\Z)"
    )
    match = pattern.search(block)
    if not match:
        return ""
    return _clean_text(match.group(1))


def _grounded_url_for_seed(
    seed: dict[str, Any],
    grounding_metadata: Any,
    used_urls: set[str],
) -> str:
    if not isinstance(grounding_metadata, dict):
        return ""
    chunks = grounding_metadata.get("groundingChunks", [])
    supports = grounding_metadata.get("groundingSupports", [])
    if not isinstance(chunks, list) or not isinstance(supports, list):
        return ""

    seed_start = seed.get("start")
    seed_end = seed.get("end")
    if not isinstance(seed_start, int) or not isinstance(seed_end, int):
        return ""

    for support in supports:
        if not isinstance(support, dict):
            continue
        segment = support.get("segment")
        if not isinstance(segment, dict):
            continue
        support_start = segment.get("startIndex", 0)
        support_end = segment.get("endIndex")
        if not isinstance(support_start, int) or not isinstance(support_end, int):
            continue
        if support_end <= seed_start or support_start >= seed_end:
            continue
        for chunk_index in support.get("groundingChunkIndices", []):
            url = _chunk_url(chunks, chunk_index)
            if url and url not in used_urls:
                return url
    return ""


def _chunk_url(chunks: Any, chunk_index: Any) -> str:
    if not isinstance(chunk_index, int):
        return ""
    if chunk_index < 0 or chunk_index >= len(chunks):
        return ""
    chunk = chunks[chunk_index]
    if not isinstance(chunk, dict):
        return ""
    web = chunk.get("web")
    if not isinstance(web, dict):
        return ""
    uri = web.get("uri")
    if not isinstance(uri, str) or not uri:
        return ""
    return sanitize_url(uri)


def _grounding_urls(grounding_metadata: Any) -> list[str]:
    if not isinstance(grounding_metadata, dict):
        return []
    urls: list[str] = []
    chunks = grounding_metadata.get("groundingChunks", [])
    if not isinstance(chunks, list):
        return []
    for index in range(len(chunks)):
        url = _chunk_url(chunks, index)
        if url and url not in urls:
            urls.append(url)
    return urls


def _gemini_search_context(grounding_metadata: Any) -> dict[str, Any] | None:
    if not isinstance(grounding_metadata, dict):
        return None

    context: dict[str, Any] = {}
    queries = grounding_metadata.get("webSearchQueries")
    if isinstance(queries, list):
        context["webSearchQueries"] = [
            query for query in queries[:SEARCH_CONTEXT_LIMIT] if isinstance(query, str)
        ]

    chunks = grounding_metadata.get("groundingChunks")
    if isinstance(chunks, list):
        compact_chunks = []
        for index, chunk in enumerate(chunks[:SEARCH_CONTEXT_LIMIT]):
            if not isinstance(chunk, dict):
                continue
            web = chunk.get("web")
            if not isinstance(web, dict):
                continue
            compact_chunks.append(
                {
                    "index": index,
                    "title": _clean_text(web.get("title")),
                    "uri": sanitize_url(web.get("uri", "")) if isinstance(web.get("uri"), str) else "",
                }
            )
        context["groundingChunks"] = compact_chunks

    supports = grounding_metadata.get("groundingSupports")
    if isinstance(supports, list):
        compact_supports = []
        for support in supports[:SEARCH_CONTEXT_LIMIT]:
            if not isinstance(support, dict):
                continue
            segment = support.get("segment")
            if not isinstance(segment, dict):
                continue
            compact_supports.append(
                {
                    "startIndex": segment.get("startIndex", 0),
                    "endIndex": segment.get("endIndex"),
                    "text_preview": bounded_preview(segment.get("text", ""), 500),
                    "groundingChunkIndices": support.get("groundingChunkIndices", []),
                }
            )
        context["groundingSupports"] = compact_supports

    search_entry_point = grounding_metadata.get("searchEntryPoint")
    if isinstance(search_entry_point, dict):
        rendered_content = search_entry_point.get("renderedContent")
        if isinstance(rendered_content, str):
            context["searchEntryPoint"] = {
                "renderedContent_preview": bounded_preview(rendered_content, 1000)
            }

    return context or None


def _clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


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


def _model_parse_context(
    provider_name: str,
    model_name: str,
    request: urllib.request.Request,
    response_text: str,
    parse_error_message: str,
    provider_response: Any,
) -> dict[str, Any]:
    context: dict[str, Any] = {
        "failure_category": "model_output_parse",
        "provider_name": provider_name,
        "model_name": model_name,
        "endpoint_url": request.full_url,
        "http_method": request.get_method(),
        "raw_model_text_preview": response_text,
        "parse_error_message": parse_error_message,
    }
    if not response_text:
        context["provider_response_preview"] = provider_response
    return context


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
