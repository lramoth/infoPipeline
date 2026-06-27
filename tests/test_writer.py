"""Tests for the Writer pipeline stage."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

import writer as writer_module
from planner import Planner, Stage
from writer import Writer, WriterError


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def make_ollama_response(message: str) -> bytes:
    return json.dumps({"model": "gemma4:e4b", "response": message}).encode("utf-8")


def make_notes_response(notes: list[str]) -> bytes:
    return make_ollama_response(json.dumps(notes))


def make_wrapped_notes_response(notes: list[str]) -> bytes:
    return make_ollama_response(f"```json\n{json.dumps(notes)}\n```")


def make_explained_notes_response(notes: list[str]) -> bytes:
    return make_ollama_response(
        "Here are the generated notes:\n"
        f"{json.dumps(notes)}\n"
        "These match the requested item order."
    )


def make_curator_item(rank: int, url: str | None = None) -> dict:
    return {
        "title": f"Item Title {rank}",
        "url": url or f"https://example.com/{rank}",
        "summary": f"Summary {rank}.",
        "curation_reason": f"Reason {rank}.",
        "rank": rank,
    }


def make_outbound_message(items: list[dict]) -> str:
    """Build a synthetic outbound message in the given item order."""
    lines = ["Daily Briefing", ""]
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
        self.prompt_path = Path(self.temporary_directory.name) / "outbound_brief.md"
        self.prompt_path.write_text("You are an outbound writer.", encoding="utf-8")
        self.template_path = Path(self.temporary_directory.name) / "template.md"
        self.template_path.write_text(
            "\n".join(
                [
                    "# Message Template",
                    "",
                    "Daily briefing",
                    "",
                    "{items}",
                    "",
                    "# Item Template",
                    "",
                    "• {title}",
                    "",
                    "{note}",
                    "",
                    "Source:",
                    "{url}",
                ]
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_sends_curator_items_and_prompt_to_ollama_and_returns_message(self):
        items = [make_curator_item(1), make_curator_item(2)]
        notes = ["First generated note.", "Second generated note."]

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_notes_response(notes)),
        ) as urlopen:
            result = Writer(prompt_path=self.prompt_path, template_path=self.template_path).run(items)

        request_body = json.loads(urlopen.call_args.args[0].data)
        self.assertIn("You are an outbound writer.", request_body["prompt"])
        self.assertIn(json.dumps(items, indent=2), request_body["prompt"])
        self.assertIsInstance(result, str)
        self.assertIn("Daily briefing", result)
        self.assertIn(items[0]["title"], result)
        self.assertIn(items[0]["url"], result)
        self.assertIn(notes[0], result)

    def test_writer_does_not_define_path_fallbacks(self):
        self.assertFalse(hasattr(writer_module, "DEFAULT_PROMPT_PATH"))
        self.assertFalse(hasattr(writer_module, "DEFAULT_TEMPLATE_PATH"))

    def test_empty_curator_items_raises_writer_error(self):
        with self.assertRaisesRegex(WriterError, "empty"):
            Writer(prompt_path=self.prompt_path, template_path=self.template_path).run([])

    def test_missing_prompt_file_raises_writer_error(self):
        missing_path = Path(self.temporary_directory.name) / "missing.md"

        with self.assertRaisesRegex(WriterError, "could not be loaded"):
            Writer(prompt_path=missing_path, template_path=self.template_path).run([make_curator_item(1)])

    def test_empty_prompt_file_raises_writer_error(self):
        empty_path = Path(self.temporary_directory.name) / "empty.md"
        empty_path.write_text("", encoding="utf-8")

        with self.assertRaisesRegex(WriterError, "empty"):
            Writer(prompt_path=empty_path, template_path=self.template_path).run([make_curator_item(1)])

    def test_ollama_execution_failure_raises_writer_error(self):
        with patch(
            "writer.urllib.request.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            with self.assertRaisesRegex(WriterError, "Ollama model execution failed"):
                Writer(prompt_path=self.prompt_path, template_path=self.template_path).run([make_curator_item(1)])

    def test_non_ollama_provider_raises_readable_error(self):
        with self.assertRaisesRegex(WriterError, "Unsupported Writer model provider"):
            Writer(
                provider="openai",
                prompt_path=self.prompt_path,
                template_path=self.template_path,
            ).run([make_curator_item(1)])

    def test_empty_ollama_response_raises_writer_error(self):
        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_ollama_response("")),
        ):
            with self.assertRaisesRegex(WriterError, "empty"):
                Writer(prompt_path=self.prompt_path, template_path=self.template_path).run([make_curator_item(1)])

    def test_missing_template_file_raises_writer_error(self):
        missing_path = Path(self.temporary_directory.name) / "missing-template.md"

        with self.assertRaisesRegex(WriterError, "could not be loaded"):
            Writer(prompt_path=self.prompt_path, template_path=missing_path).run([make_curator_item(1)])

    def test_empty_template_file_raises_writer_error(self):
        empty_path = Path(self.temporary_directory.name) / "empty-template.md"
        empty_path.write_text("", encoding="utf-8")

        with self.assertRaisesRegex(WriterError, "Template file is empty"):
            Writer(prompt_path=self.prompt_path, template_path=empty_path).run([make_curator_item(1)])

    def test_template_missing_required_placeholder_raises_writer_error(self):
        templates = [
            ["# Message Template", "", "# Item Template", "", "{title}", "{note}", "{url}"],
            ["# Message Template", "", "{items}", "", "# Item Template", "", "{note}", "{url}"],
            ["# Message Template", "", "{items}", "", "# Item Template", "", "{title}", "{url}"],
            ["# Message Template", "", "{items}", "", "# Item Template", "", "{title}", "{note}"],
        ]

        for lines in templates:
            with self.subTest(template="\n".join(lines)):
                self.template_path.write_text("\n".join(lines), encoding="utf-8")
                with self.assertRaisesRegex(WriterError, "placeholder"):
                    Writer(prompt_path=self.prompt_path, template_path=self.template_path).run([make_curator_item(1)])

    def test_model_changed_url_is_not_authoritative(self):
        items = [
            make_curator_item(
                1,
                "https://example.com/news/label/very/long/source-slug?ref=curator",
            )
        ]

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_notes_response(["The model can mention context, but not own the source."])),
        ):
            result = Writer(prompt_path=self.prompt_path, template_path=self.template_path).run(items)

        self.assertIn(items[0]["url"], result)
        self.assertNotIn("https://example.com/news/label", result.replace(items[0]["url"], ""))

    def test_model_changed_title_is_not_authoritative(self):
        items = [make_curator_item(1)]

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_notes_response(["Wrong Title: useful context without authority."])),
        ):
            result = Writer(prompt_path=self.prompt_path, template_path=self.template_path).run(items)

        self.assertIn(items[0]["title"], result)

    def test_model_omitted_url_still_uses_curator_url(self):
        items = [make_curator_item(1)]

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_notes_response(["A concise generated note with no source link."])),
        ):
            result = Writer(prompt_path=self.prompt_path, template_path=self.template_path).run(items)

        self.assertIn(items[0]["url"], result)

    def test_items_are_assembled_in_ascending_rank_order(self):
        items = [make_curator_item(2), make_curator_item(1)]

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_notes_response(["Rank one note.", "Rank two note."])),
        ):
            result = Writer(prompt_path=self.prompt_path, template_path=self.template_path).run(items)

        self.assertLess(result.find("Item Title 1"), result.find("Item Title 2"))

    def test_custom_template_controls_outbound_presentation(self):
        items = [make_curator_item(1)]
        self.template_path.write_text(
            "\n".join(
                [
                    "# Message Template",
                    "",
                    "Custom opener",
                    "",
                    "{items}",
                    "",
                    "Custom closer",
                    "",
                    "# Item Template",
                    "",
                    "### {title}",
                    "Why it matters: {note}",
                    "Link => {url}",
                ]
            ),
            encoding="utf-8",
        )

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_notes_response(["custom note"])),
        ):
            result = Writer(prompt_path=self.prompt_path, template_path=self.template_path).run(items)

        self.assertIn("Custom opener", result)
        self.assertIn("### Item Title 1", result)
        self.assertIn("Why it matters: custom note", result)
        self.assertIn("Link => https://example.com/1", result)

    def test_accepts_model_notes_wrapped_in_markdown_code_fence(self):
        items = [make_curator_item(1)]
        notes = ["Generated note from fenced JSON."]

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_wrapped_notes_response(notes)),
        ):
            result = Writer(prompt_path=self.prompt_path, template_path=self.template_path).run(items)

        self.assertIn(notes[0], result)
        self.assertIn(items[0]["title"], result)
        self.assertIn(items[0]["url"], result)

    def test_accepts_model_notes_surrounded_by_explanatory_text(self):
        items = [make_curator_item(1)]
        notes = ["Generated note from surrounded JSON."]

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_explained_notes_response(notes)),
        ):
            result = Writer(prompt_path=self.prompt_path, template_path=self.template_path).run(items)

        self.assertIn(notes[0], result)
        self.assertIn(items[0]["title"], result)
        self.assertIn(items[0]["url"], result)

    def test_unusable_model_prose_raises_writer_error(self):
        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_ollama_response("not json")),
        ):
            with self.assertRaisesRegex(WriterError, "usable item prose"):
                Writer(prompt_path=self.prompt_path, template_path=self.template_path).run([make_curator_item(1)])

    def test_unusable_model_prose_includes_diagnostic_context(self):
        model_response = "not json"

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_ollama_response(model_response)),
        ):
            with self.assertRaisesRegex(WriterError, "usable item prose") as captured:
                Writer(prompt_path=self.prompt_path, template_path=self.template_path).run([make_curator_item(1)])

        context = captured.exception.diagnostic_context
        self.assertEqual("model_output_parse", context["failure_category"])
        self.assertEqual(model_response, context["raw_model_text_preview"])
        self.assertIn("No valid structured payload", context["parse_error_message"])

    def test_wrong_note_count_raises_writer_error(self):
        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_notes_response(["Only one note."])),
        ):
            with self.assertRaisesRegex(WriterError, "expected 2 notes"):
                Writer(prompt_path=self.prompt_path, template_path=self.template_path).run(
                    [make_curator_item(1), make_curator_item(2)]
                )

    def test_empty_or_non_text_note_raises_writer_error(self):
        responses = [
            make_ollama_response(json.dumps([""])),
            make_ollama_response(json.dumps([{"note": "not text"}])),
        ]

        for response in responses:
            with self.subTest(response=response):
                with patch(
                    "writer.urllib.request.urlopen",
                    return_value=FakeResponse(response),
                ):
                    with self.assertRaisesRegex(WriterError, "usable item prose"):
                        Writer(prompt_path=self.prompt_path, template_path=self.template_path).run([make_curator_item(1)])

    def test_unusable_model_prose_diagnostic_records_model_output_preview(self):
        model_response = "Here are notes, but not as structured data."

        writer = Writer(prompt_path=self.prompt_path, template_path=self.template_path)
        planner = Planner(
            stages=[
                Stage(
                    "curator",
                    lambda: [make_curator_item(1)],
                    lambda output: (True, "Curated items are available"),
                ),
                writer,
            ],
            ledger_path=Path(self.temporary_directory.name) / "output" / "ledger.json",
        )

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_ollama_response(model_response)),
        ):
            result = planner.run()

        self.assertFalse(result.succeeded)
        ledger = json.loads(planner.ledger_path.read_text(encoding="utf-8"))
        writer_entry = ledger["stages"]["writer"]
        diagnostic_file = Path(writer_entry["diagnostic_path"])
        diagnostic = json.loads(diagnostic_file.read_text(encoding="utf-8"))

        self.assertTrue(diagnostic_file.exists())
        self.assertEqual("model_output_parse", diagnostic["failure_category"])
        self.assertIn(model_response, diagnostic["raw_model_text_preview"])
        self.assertIn("parse_error_message", diagnostic)
        self.assertNotIn("api_key", json.dumps(diagnostic).lower())

    def test_validation_succeeds_for_complete_message_with_all_items(self):
        items = [make_curator_item(1), make_curator_item(2)]
        message = make_outbound_message(sorted(items, key=lambda x: x["rank"]))

        passed, reason = Writer.validate(message, items)

        self.assertTrue(passed, reason)

    def test_validation_succeeds_when_items_share_url_in_each_section(self):
        shared_url = "https://example.com/shared-source"
        items = [make_curator_item(1, shared_url), make_curator_item(2, shared_url)]
        message = make_outbound_message(sorted(items, key=lambda x: x["rank"]))

        passed, reason = Writer.validate(message, items)

        self.assertTrue(passed, reason)

    def test_validation_fails_when_shared_url_is_missing_from_one_item_section(self):
        shared_url = "https://example.com/shared-source"
        items = [make_curator_item(1, shared_url), make_curator_item(2, shared_url)]
        message = "\n".join(
            [
                "Daily Briefing",
                "",
                f"• {items[0]['title']}",
                "",
                "Some summary text about this item.",
                "",
                "Source:",
                shared_url,
                "",
                f"• {items[1]['title']}",
                "",
                "Some summary text about this item.",
            ]
        )

        passed, reason = Writer.validate(message, items)

        self.assertFalse(passed)
        self.assertIn("URL", reason)

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
        message = make_outbound_message(sorted(items, key=lambda x: x["rank"], reverse=True))

        passed, reason = Writer.validate(message, items)

        self.assertFalse(passed)
        self.assertIn("rank", reason)

    def test_loads_configured_prompt_at_run_time(self):
        items = [make_curator_item(1)]
        self.prompt_path.write_text("updated writer prompt", encoding="utf-8")

        with patch(
            "writer.urllib.request.urlopen",
            return_value=FakeResponse(make_notes_response(["Generated note."])),
        ) as urlopen:
            Writer(prompt_path=self.prompt_path, template_path=self.template_path).run(items)

        request_body = json.loads(urlopen.call_args.args[0].data)
        self.assertIn("updated writer prompt", request_body["prompt"])


if __name__ == "__main__":
    unittest.main()
