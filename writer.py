"""Local Ollama writer for the Writer pipeline stage."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from diagnostics import DiagnosticError, external_http_context
from prompt_loader import PromptLoadError, load_prompt


OLLAMA_MODEL = "gemma4:e4b"
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
DEFAULT_PROMPT_PATH = Path(__file__).parent / "prompts" / "writers" / "outbound_brief.md"
DEFAULT_TEMPLATE_PATH = Path(__file__).parent / "prompts" / "writers" / "template.md"


class WriterError(DiagnosticError):
    """Raised when the Writer cannot produce an outbound message."""


class Writer:
    """Format curated items into an outbound message via local Ollama."""

    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        endpoint: str = OLLAMA_ENDPOINT,
        prompt_path: str | Path = DEFAULT_PROMPT_PATH,
        template_path: str | Path = DEFAULT_TEMPLATE_PATH,
    ) -> None:
        self.model = model
        self.endpoint = endpoint
        self.prompt_path = Path(prompt_path)
        self.template_path = Path(template_path)

    def run(self, items: list[dict[str, Any]]) -> str:
        """Format curated items into an outbound message and return it."""
        if not items:
            raise WriterError("Curator output is empty — no items to format")

        try:
            prompt_content = load_prompt(self.prompt_path)
        except PromptLoadError as error:
            raise WriterError(str(error)) from error

        if not prompt_content.strip():
            raise WriterError(f"Prompt file is empty: {self.prompt_path}")

        try:
            template_content = load_prompt(self.template_path)
        except PromptLoadError as error:
            raise WriterError(str(error)) from error

        message_template, item_template = self._parse_template(template_content)
        sorted_items = sorted(items, key=lambda item: item["rank"])

        full_prompt = f"{prompt_content}\n\nCurated items:\n{json.dumps(sorted_items, indent=2)}"
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
        except urllib.error.URLError as error:
            raise WriterError(
                f"Ollama model execution failed: {error}",
                external_http_context("Ollama", self.model, request, error),
            ) from error
        except json.JSONDecodeError as error:
            raise WriterError(
                f"Ollama model execution failed: {error}",
                {
                    "failure_category": "external_http_call",
                    "provider_name": "Ollama",
                    "model_name": self.model,
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "parse_error_message": str(error),
                },
            ) from error

        message = api_response.get("response", "")
        if not message or not message.strip():
            raise WriterError("Ollama returned an empty response")

        notes = self._parse_notes(message, len(sorted_items))
        outbound_message = self._assemble_message(message_template, item_template, sorted_items, notes)

        is_valid, reason = self.validate(outbound_message, sorted_items)
        if not is_valid:
            raise WriterError(f"Final outbound message failed validation: {reason}")

        return outbound_message

    def _parse_template(self, template_content: str) -> tuple[str, str]:
        if not template_content.strip():
            raise WriterError(f"Template file is empty: {self.template_path}")

        lines = template_content.splitlines()
        separator_index = next(
            (index for index, line in enumerate(lines) if line.strip() == "# Item Template"),
            None,
        )
        if separator_index is None:
            raise WriterError("Template is missing required item template section")

        message_lines = lines[:separator_index]
        item_lines = lines[separator_index + 1 :]

        if message_lines and message_lines[0].strip() == "# Message Template":
            message_lines = message_lines[1:]

        message_template = "\n".join(message_lines).strip()
        item_template = "\n".join(item_lines).strip()

        missing_placeholders = []
        if "{items}" not in message_template:
            missing_placeholders.append("{items}")
        for placeholder in ("{title}", "{note}", "{url}"):
            if placeholder not in item_template:
                missing_placeholders.append(placeholder)

        if missing_placeholders:
            joined = ", ".join(missing_placeholders)
            raise WriterError(f"Template is missing required placeholder(s): {joined}")

        return message_template, item_template

    @staticmethod
    def _parse_notes(model_response: str, expected_count: int) -> list[str]:
        try:
            parsed = json.loads(model_response)
        except json.JSONDecodeError as error:
            raise WriterError(f"Ollama returned no usable item prose: {error}") from error

        if not isinstance(parsed, list):
            raise WriterError("Ollama returned no usable item prose: expected a JSON array")

        notes = []
        for note in parsed:
            if not isinstance(note, str) or not note.strip():
                raise WriterError("Ollama returned no usable item prose")
            notes.append(note.strip())

        if len(notes) != expected_count:
            raise WriterError(
                f"Ollama returned no usable item prose: expected {expected_count} notes, got {len(notes)}"
            )

        return notes

    @staticmethod
    def _assemble_message(
        message_template: str,
        item_template: str,
        items: list[dict[str, Any]],
        notes: list[str],
    ) -> str:
        rendered_items = []
        for item, note in zip(items, notes):
            rendered_items.append(
                item_template.format(
                    title=item.get("title", ""),
                    note=note,
                    url=item.get("url", ""),
                )
            )

        return message_template.format(items="\n\n".join(rendered_items)).strip()

    @staticmethod
    def validate(output: Any, items: list[dict[str, Any]]) -> tuple[bool, str]:
        """Validate that the message contains all curator items in ascending rank order."""
        if not isinstance(output, str):
            return False, "Writer output is not a string"

        sorted_items = sorted(items, key=lambda item: item["rank"])
        title_positions = []

        for item in sorted_items:
            title = item.get("title", "")

            title_pos = output.find(title)
            if title_pos == -1:
                return False, f"Item title missing from outbound message: {title!r}"

            title_positions.append(title_pos)

        for i in range(1, len(title_positions)):
            if title_positions[i] <= title_positions[i - 1]:
                prev_rank = sorted_items[i - 1]["rank"]
                curr_rank = sorted_items[i]["rank"]
                return False, f"Items are not in ascending rank order: rank {curr_rank} appears before rank {prev_rank}"

        for index, item in enumerate(sorted_items):
            title = item.get("title", "")
            url = item.get("url", "")
            title_pos = title_positions[index]
            section_start = title_pos + len(title)
            section_end = (
                title_positions[index + 1]
                if index + 1 < len(title_positions)
                else len(output)
            )
            section = output[section_start:section_end]

            if section.find(url) == -1:
                return False, f"Item URL missing from outbound message: {url!r}"

            if not Writer._section_has_readable_prose(section, title, url):
                return False, f"Item is missing summary text in outbound message: {title!r}"

        return True, "Outbound message contains all curator items in ascending rank order with title, URL, and summary"

    @staticmethod
    def _section_has_readable_prose(section: str, title: str, url: str) -> bool:
        remainder = section.replace(title, "").replace(url, "")
        for line in remainder.splitlines():
            text = line.strip().strip("*_-•#`[]()")
            if not text:
                continue
            if text.endswith(":"):
                continue
            if any(character.isalnum() for character in text):
                return True
        return False
