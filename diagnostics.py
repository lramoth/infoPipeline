"""Best-effort local diagnostic records for failed pipeline stages."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


PREVIEW_LIMIT = 2000
SECRET_QUERY_NAMES = {
    "api_key",
    "apikey",
    "key",
    "token",
    "access_token",
    "auth",
    "authorization",
    "chat_id",
}
SECRET_VALUE_PATTERN = re.compile(
    r"(?i)(api[_-]?key|token|chat[_-]?id|authorization)"
    r"([\"'\s:=]+)"
    r"([\"']?)[^\"'\s,}]+"
)


class DiagnosticError(RuntimeError):
    """Runtime error that carries structured diagnostic context."""

    def __init__(
        self,
        message: str,
        diagnostic_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.diagnostic_context = diagnostic_context or {}


def bounded_preview(value: Any, limit: int = PREVIEW_LIMIT) -> str:
    """Return a fixed-size human-readable preview of a diagnostic value."""
    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, ensure_ascii=False, indent=2)
        except (TypeError, ValueError):
            text = str(value)

    text = SECRET_VALUE_PATTERN.sub(r"\1\2\3[redacted]", text)
    if len(text) <= limit:
        return text
    return text[:limit] + "...[truncated]"


def sanitize_url(url: str) -> str:
    """Remove common secret-bearing query parameters from a URL."""
    parsed = urlsplit(url)
    safe_query = urlencode(
        [
            (name, value)
            for name, value in parse_qsl(parsed.query, keep_blank_values=True)
            if name.lower() not in SECRET_QUERY_NAMES
        ],
        doseq=True,
    )
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, safe_query, parsed.fragment))


def write_diagnostic(
    diagnostics_root: str | Path,
    stage_name: str,
    failure_category: str,
    error_type: str,
    error_message: str,
    context: dict[str, Any] | None = None,
    timestamp: datetime | None = None,
) -> Path:
    """Write a JSON diagnostic file and return its path."""
    timestamp = timestamp or datetime.now(timezone.utc)
    day = timestamp.date().isoformat()
    file_stamp = timestamp.strftime("%Y%m%dT%H%M%S%fZ")
    safe_stage_name = "".join(
        character if character.isalnum() or character in ("-", "_") else "-"
        for character in stage_name.lower()
    ).strip("-") or "stage"
    diagnostic_dir = Path(diagnostics_root) / day
    diagnostic_dir.mkdir(parents=True, exist_ok=True)
    diagnostic_path = diagnostic_dir / f"{safe_stage_name}-{file_stamp}.json"

    record: dict[str, Any] = {
        "stage_name": stage_name,
        "timestamp": timestamp.isoformat(),
        "failure_category": failure_category,
        "error_type": error_type,
        "error_message": bounded_preview(error_message),
    }
    if context:
        record.update(_sanitize_context(context))

    with diagnostic_path.open("w", encoding="utf-8") as diagnostic_file:
        json.dump(record, diagnostic_file, indent=2, ensure_ascii=False)
        diagnostic_file.write("\n")

    return diagnostic_path


def external_http_context(
    provider_name: str,
    model_name: str,
    request: urllib.request.Request,
    error: BaseException,
) -> dict[str, Any]:
    """Return diagnostic context for a failed external HTTP call."""
    context: dict[str, Any] = {
        "failure_category": "external_http_call",
        "provider_name": provider_name,
        "model_name": model_name,
        "endpoint_url": sanitize_url(request.full_url),
        "http_method": request.get_method(),
    }
    if isinstance(error, urllib.error.HTTPError):
        context["response_status"] = error.code
        response_body = error.read()
        if response_body:
            context["response_body_preview"] = response_body.decode(
                "utf-8",
                errors="replace",
            )
    return context


def _sanitize_context(context: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in context.items():
        if key == "endpoint_url" and isinstance(value, str):
            sanitized[key] = sanitize_url(value)
        elif key.endswith("_preview"):
            sanitized[key] = bounded_preview(value)
        elif key in {"response_body", "raw_model_text", "invalid_stage_output"}:
            sanitized[f"{key}_preview"] = bounded_preview(value)
        else:
            sanitized[key] = value
    return sanitized
