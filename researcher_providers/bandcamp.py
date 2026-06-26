"""Bandcamp Discover-backed Researcher provider behavior."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from diagnostics import bounded_preview
from researcher_providers.errors import ResearcherError


BANDCAMP_DISCOVER_ENDPOINT = "https://bandcamp.com/api/discover/1/discover_web"
BANDCAMP_DISCOVER_PAYLOAD = {
    "category_id": 0,
    "tag_norm_names": ["hypnotic-techno", "techno"],
    "geoname_id": 0,
    "slice": "new",
    "time_facet_id": 0,
    "cursor": "*",
    "size": 24,
    "include_result_types": ["a", "s"],
}
RAW_PROVIDER_RESPONSE_LIMIT = 12000


class BandcampResearcherProvider:
    """Collect new Bandcamp Discover items and normalize them for Researcher."""

    def run(self) -> dict[str, Any]:
        request = urllib.request.Request(
            BANDCAMP_DISCOVER_ENDPOINT,
            data=json.dumps(BANDCAMP_DISCOVER_PAYLOAD).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request) as response:
                api_response = json.load(response)
        except urllib.error.URLError as error:
            raise ResearcherError(
                f"Bandcamp Discover request failed: {error}",
                _http_context(request, str(error)),
            ) from error
        except json.JSONDecodeError as error:
            raise ResearcherError(
                f"Bandcamp Discover response was malformed: {error}",
                _parse_context(request, str(error), None),
            ) from error

        try:
            results = api_response["results"]
            if not isinstance(results, list):
                raise TypeError("Bandcamp results is not a list")
        except (KeyError, TypeError) as error:
            raise ResearcherError(
                f"Bandcamp Discover response was malformed: {error}",
                _parse_context(request, str(error), api_response),
            ) from error

        return {
            "items": _normalize_results(results),
            "raw_provider_response": {
                "provider": "Bandcamp",
                "endpoint_url": request.full_url,
                "request_body": BANDCAMP_DISCOVER_PAYLOAD,
                "response_preview": bounded_preview(
                    api_response,
                    RAW_PROVIDER_RESPONSE_LIMIT,
                ),
            },
            "normalization": {
                "source": "bandcamp_discover",
                "url_source": "item_url",
            },
        }


def _normalize_results(results: list[Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    used_urls: set[str] = set()
    for result in results:
        if not isinstance(result, dict):
            continue
        item = _normalize_result(result)
        if item is None or item["url"] in used_urls:
            continue
        items.append(item)
        used_urls.add(item["url"])
    return items


def _normalize_result(result: dict[str, Any]) -> dict[str, str] | None:
    title = _clean_text(result.get("title"))
    url = _clean_url(result.get("item_url"))
    summary = _summary(result)
    if not title or not url or not summary:
        return None

    artist = _clean_text(result.get("album_artist"))
    normalized_title = f"{artist} - {title}" if artist else title
    return {
        "title": normalized_title,
        "url": url,
        "summary": summary,
    }


def _summary(result: dict[str, Any]) -> str:
    artist = _clean_text(result.get("album_artist"))
    title = _clean_text(result.get("title"))
    band_name = _clean_text(result.get("band_name"))
    location = _clean_text(result.get("band_location"))
    release_date = _release_date(result.get("release_date"))
    track_count = result.get("track_count")
    featured_track = result.get("featured_track")
    featured_title = (
        _clean_text(featured_track.get("title"))
        if isinstance(featured_track, dict)
        else ""
    )
    package_formats = _package_formats(result.get("package_info"))

    if not title:
        return ""

    parts = []
    if release_date:
        parts.append(f"{release_date} Bandcamp release")
    else:
        parts.append("Bandcamp release")
    if artist:
        parts.append(f"by {artist}")
    if band_name:
        parts.append(f"on {band_name}")
    if location:
        parts.append(f"from {location}")
    if isinstance(track_count, int) and track_count > 0:
        parts.append(f"with {track_count} tracks")
    if featured_title:
        parts.append(f"featuring {featured_title}")
    if package_formats:
        parts.append(f"available as {package_formats}")

    return " ".join(parts) + "."


def _clean_url(value: Any) -> str:
    url = _clean_text(value)
    if not url:
        return ""
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, "", parsed.fragment)
    )


def _release_date(value: Any) -> str:
    text = _clean_text(value)
    if len(text) >= 10:
        return text[:10]
    return ""


def _package_formats(value: Any) -> str:
    if not isinstance(value, list):
        return ""
    formats = []
    for package in value:
        if not isinstance(package, dict):
            continue
        package_format = _clean_text(package.get("format"))
        if package_format and package_format not in formats:
            formats.append(package_format)
    return ", ".join(formats)


def _clean_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _http_context(
    request: urllib.request.Request,
    error_message: str,
) -> dict[str, Any]:
    return {
        "failure_category": "external_http_call",
        "provider_name": "Bandcamp",
        "endpoint_url": request.full_url,
        "http_method": request.get_method(),
        "error_message": error_message,
    }


def _parse_context(
    request: urllib.request.Request,
    parse_error_message: str,
    provider_response: Any,
) -> dict[str, Any]:
    context: dict[str, Any] = {
        "failure_category": "provider_response_parse",
        "provider_name": "Bandcamp",
        "endpoint_url": request.full_url,
        "http_method": request.get_method(),
        "parse_error_message": parse_error_message,
    }
    if provider_response is not None:
        context["provider_response_preview"] = bounded_preview(
            provider_response,
            RAW_PROVIDER_RESPONSE_LIMIT,
        )
    return context
