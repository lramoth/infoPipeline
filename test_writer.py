"""Tests for the Writer pipeline stage."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from writer import Writer, WriterError


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def make_ollama_response(message: str) -> bytes:
    return json.dumps({"model": "gemma4:e4b", "response": message}).encode("utf-8")


def make_curator_item(rank: int, url: str | None = None) -> dict:
    return {
        "title": f"Item Title {rank}",
        "url": url or f"https://example.com/{rank}",
        "summary": f"Summary {rank}.",
        "curation_reason": f"Reason {rank}.",
        "rank": rank,
    }


def make_telegram_message(items: list[dict]) -> str:
    """Build a synthetic Telegram message in the given item order."""
    lines = ["🎛 Techno Briefing", ""]
    for item in items:
        lines.append(f"• {item['title']}")
        lines.append("")
        lines.append("Some summary text about this item.")
        lines.append("")
        lines.append("Source:")
        lines.append(item["url"])
        lines.append("")
    return "\n".join(lines)


class WriterTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.prompt_path = Path(self.temporary_directory.name) / "telegram_brief.md"
        self.prompt_path.write_text("You are a Telegram writer.", encoding="utf-8")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_sends_curator_items_and_prompt_to_ollama_and_returns_message(self):
        items = [make_curator_item(1), make_curator_item(2)]
        message = make_telegram_message(sorted(items, key=lambda x: x["rank"]))

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_ollama_response(message)),
        ) as urlopen:
            result = Writer(prompt_path=self.prompt_path).run(items)

        request_body = json.loads(urlopen.call_args.args[0].data)
        self.assertIn("You are a Telegram writer.", request_body["prompt"])
        self.assertIn(json.dumps(items, indent=2), request_body["prompt"])
        self.assertIsInstance(result, str)
        self.assertEqual(result, message)

    def test_uses_default_prompt_when_no_prompt_path_given(self):
        items = [make_curator_item(1)]
        message = make_telegram_message(items)

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_ollama_response(message)),
        ) as urlopen:
            Writer().run(items)

        request_body = json.loads(urlopen.call_args.args[0].data)
        self.assertIn("Telegram briefing", request_body["prompt"])

    def test_empty_curator_items_raises_writer_error(self):
        with self.assertRaisesRegex(WriterError, "empty"):
            Writer(prompt_path=self.prompt_path).run([])

    def test_missing_prompt_file_raises_writer_error(self):
        missing_path = Path(self.temporary_directory.name) / "missing.md"

        with self.assertRaisesRegex(WriterError, "could not be loaded"):
            Writer(prompt_path=missing_path).run([make_curator_item(1)])

    def test_empty_prompt_file_raises_writer_error(self):
        empty_path = Path(self.temporary_directory.name) / "empty.md"
        empty_path.write_text("", encoding="utf-8")

        with self.assertRaisesRegex(WriterError, "empty"):
            Writer(prompt_path=empty_path).run([make_curator_item(1)])

    def test_ollama_execution_failure_raises_writer_error(self):
        with patch(
            "writer.urllib.request.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            with self.assertRaisesRegex(WriterError, "Ollama model execution failed"):
                Writer(prompt_path=self.prompt_path).run([make_curator_item(1)])

    def test_empty_ollama_response_raises_writer_error(self):
        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_ollama_response("")),
        ):
            with self.assertRaisesRegex(WriterError, "empty"):
                Writer(prompt_path=self.prompt_path).run([make_curator_item(1)])

    def test_validation_succeeds_for_complete_message_with_all_items(self):
        items = [make_curator_item(1), make_curator_item(2)]
        message = make_telegram_message(sorted(items, key=lambda x: x["rank"]))

        passed, reason = Writer.validate(message, items)

        self.assertTrue(passed, reason)

    def test_validation_fails_when_output_is_not_a_string(self):
        passed, reason = Writer.validate(["not", "a", "string"], [make_curator_item(1)])

        self.assertFalse(passed)

    def test_validation_fails_when_item_url_is_missing(self):
        items = [make_curator_item(1)]
        message = f"• {items[0]['title']}\n\nSome summary text.\n\nSource:\nhttps://other.example.com/wrong"

        passed, reason = Writer.validate(message, items)

        self.assertFalse(passed)
        self.assertIn("URL", reason)

    def test_validation_fails_when_item_title_is_missing(self):
        items = [make_curator_item(1)]
        message = f"• Wrong Title\n\nSome summary text.\n\nSource:\n{items[0]['url']}"

        passed, reason = Writer.validate(message, items)

        self.assertFalse(passed)
        self.assertIn("title", reason)

    def test_validation_fails_when_item_summary_is_missing(self):
        items = [make_curator_item(1)]
        message = f"• {items[0]['title']}\nSource:\n{items[0]['url']}"

        passed, reason = Writer.validate(message, items)

        self.assertFalse(passed)
        self.assertIn("summary", reason)

    def test_validation_fails_when_items_are_not_in_ascending_rank_order(self):
        items = [make_curator_item(1), make_curator_item(2)]
        message = make_telegram_message(sorted(items, key=lambda x: x["rank"], reverse=True))

        passed, reason = Writer.validate(message, items)

        self.assertFalse(passed)
        self.assertIn("rank", reason)

    def test_loads_configured_prompt_at_run_time(self):
        items = [make_curator_item(1)]
        message = make_telegram_message(items)
        self.prompt_path.write_text("updated writer prompt", encoding="utf-8")

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_ollama_response(message)),
        ) as urlopen:
            Writer(prompt_path=self.prompt_path).run(items)

        request_body = json.loads(urlopen.call_args.args[0].data)
        self.assertIn("updated writer prompt", request_body["prompt"])


if __name__ == "__main__":
    unittest.main()
