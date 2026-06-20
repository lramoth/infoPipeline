"""Gemini search-grounded collector for the Researcher pipeline stage."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"

RESEARCH_PROMPT = """You are a research assistant finding current techno production news.

Search for recent news (last 7 days) about:
- Techno record labels and new releases (Polegroup-adjacent labels especially: Polegroup and similar minimal/hypnotic/raw aesthetic)
- New hardware releases like synths, drum machines, sequencers. (Companies like Roland, Elektron, Korg, Moog and Eurorack manufacturers are good candidates)
- Notable techno artist news (new EPs,  label signings — not festival lineups or general EDM news)

Respond with ONLY a JSON array, no other text, no markdown formatting, no 
code fences. Each item must have exactly these fields:

[
  {"title": "short headline", "url": "https://...", "summary": "one sentence"}
]

If you find fewer than 3 genuinely relevant items, return only the ones that 
are real and relevant — do not invent items to reach a count."""


class ResearcherError(RuntimeError):
    """Raised when Gemini search cannot produce research output."""


class Researcher:
    """Collect and validate recent techno-production research from Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = GEMINI_MODEL,
        endpoint: str = GEMINI_ENDPOINT,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("GEMINI_API_KEY")
        self.model = model
        self.endpoint = endpoint.rstrip("/")

    def run(self) -> dict[str, Any]:
        """Search Gemini without Planner input and return items plus grounding data."""
        if not self.api_key:
            raise ResearcherError("GEMINI_API_KEY is not set")

        payload = {
            "contents": [{"parts": [{"text": RESEARCH_PROMPT}]}],
            "tools": [{"google_search": {}}],
        }
        request = urllib.request.Request(
            f"{self.endpoint}/{self.model}:generateContent",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request) as response:
                api_response = json.load(response)
        except (urllib.error.URLError, json.JSONDecodeError) as error:
            raise ResearcherError(f"Gemini API search failed: {error}") from error

        try:
            candidate = api_response["candidates"][0]
            response_text = "".join(
                part.get("text", "") for part in candidate["content"]["parts"]
            )
            items = json.loads(response_text)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise ResearcherError(f"Invalid Gemini API search response: {error}") from error

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

