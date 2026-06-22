"""Local Ollama writer for the Writer pipeline stage."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from prompt_loader import PromptLoadError, load_prompt


OLLAMA_MODEL = "gemma4:e4b"
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
DEFAULT_PROMPT_PATH = Path(__file__).parent / "prompts" / "writers" / "telegram_brief.md"


class WriterError(RuntimeError):
    """Raised when the Writer cannot produce a Telegram message."""


class Writer:
    """Format curated items into a Telegram-ready message via local Ollama."""

    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        endpoint: str = OLLAMA_ENDPOINT,
        prompt_path: str | Path = DEFAULT_PROMPT_PATH,
    ) -> None:
        self.model = model
        self.endpoint = endpoint
        self.prompt_path = Path(prompt_path)

    def run(self, items: list[dict[str, Any]]) -> str:
        """Format curated items into a Telegram message and return it."""
        if not items:
            raise WriterError("Curator output is empty — no items to format")

        try:
            prompt_content = load_prompt(self.prompt_path)
        except PromptLoadError as error:
            raise WriterError(str(error)) from error

        if not prompt_content.strip():
            raise WriterError(f"Prompt file is empty: {self.prompt_path}")

        full_prompt = f"{prompt_content}\n\nCurated items:\n{json.dumps(items, indent=2)}"
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request) as response:
                api_response = json.load(response)
        except (urllib.error.URLError, json.JSONDecodeError) as error:
            raise WriterError(f"Ollama model execution failed: {error}") from error

        message = api_response.get("response", "")
        if not message or not message.strip():
            raise WriterError("Ollama returned an empty response")

        return message

    @staticmethod
    def validate(output: Any, items: list[dict[str, Any]]) -> tuple[bool, str]:
        """Validate that the message contains all curator items in ascending rank order."""
        if not isinstance(output, str):
            return False, "Writer output is not a string"

        sorted_items = sorted(items, key=lambda item: item["rank"])
        url_positions = []

        for item in sorted_items:
            title = item.get("title", "")
            url = item.get("url", "")

            url_pos = output.find(url)
            if url_pos == -1:
                return False, f"Item URL missing from Telegram message: {url!r}"

            title_pos = output.rfind(title, 0, url_pos)
            if title_pos == -1:
                return False, f"Item title missing from Telegram message: {title!r}"

            between = output[title_pos + len(title):url_pos].strip()
            between_cleaned = between.replace("Source:", "").strip()
            if not between_cleaned:
                return False, f"Item is missing summary text in Telegram message: {title!r}"

            url_positions.append(url_pos)

        for i in range(1, len(url_positions)):
            if url_positions[i] <= url_positions[i - 1]:
                prev_rank = sorted_items[i - 1]["rank"]
                curr_rank = sorted_items[i]["rank"]
                return False, f"Items are not in ascending rank order: rank {curr_rank} appears before rank {prev_rank}"

        return True, "Telegram message contains all curator items in ascending rank order with title, URL, and summary"
