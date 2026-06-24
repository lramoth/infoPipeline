from __future__ import annotations

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from researcher import Researcher, ResearcherError


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def make_api_response(model_text: str, grounding_metadata: dict | None = None) -> bytes:
    candidate = {"content": {"parts": [{"text": model_text}]}}
    if grounding_metadata is not None:
        candidate["groundingMetadata"] = grounding_metadata
    return json.dumps({"candidates": [candidate]}).encode("utf-8")


def make_openai_response(model_text: str) -> bytes:
    return json.dumps(
        {
            "output": [
                {"type": "web_search_call", "id": "search_1", "status": "completed"},
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": model_text}],
                },
            ]
        }
    ).encode("utf-8")


class ResearcherTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.env_path = Path(self.temporary_directory.name) / ".env"
        self.env_path.write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")
        self.prompt_path = Path(self.temporary_directory.name) / "research.md"
        self.prompt_path.write_text("custom research prompt", encoding="utf-8")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_searches_gemini_and_preserves_grounding_metadata(self):
        items = [
            {"title": f"Item {number}", "url": f"https://example.com/{number}", "summary": "News."}
            for number in range(3)
        ]
        grounding_metadata = {
            "groundingChunks": [{"web": {"uri": "https://example.com/source"}}]
        }
        response = {
            "candidates": [
                {
                    "content": {"parts": [{"text": json.dumps(items)}]},
                    "groundingMetadata": grounding_metadata,
                }
            ]
        }

        with patch(
            "researcher.urllib.request.urlopen",
            return_value=FakeResponse(json.dumps(response).encode("utf-8")),
        ) as urlopen:
            output = Researcher(env_path=self.env_path, prompt_path=self.prompt_path).run()

        request = urlopen.call_args.args[0]
        self.assertEqual(request.headers["X-goog-api-key"], "test-key")
        request_body = json.loads(request.data)
        self.assertEqual(request_body["contents"][0]["parts"][0]["text"], "custom research prompt")
        self.assertEqual(request_body["tools"], [{"google_search": {}}])
        self.assertEqual(output["items"], items)
        self.assertEqual(output["grounding_metadata"], grounding_metadata)

    def test_searches_openai_with_web_search_and_returns_existing_output_contract(self):
        self.env_path.write_text("OPENAI_API_KEY=openai-key\n", encoding="utf-8")
        items = [
            {"title": f"Item {number}", "url": f"https://example.com/{number}", "summary": "News."}
            for number in range(3)
        ]

        with patch(
            "researcher.urllib.request.urlopen",
            return_value=FakeResponse(make_openai_response(json.dumps(items))),
        ) as urlopen:
            output = Researcher(
                provider="openai",
                model="gpt-4.1-mini",
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.openai.com/v1/responses")
        self.assertEqual(request.headers["Authorization"], "Bearer openai-key")
        request_body = json.loads(request.data)
        self.assertEqual(request_body["model"], "gpt-4.1-mini")
        self.assertEqual(request_body["input"], "custom research prompt")
        self.assertEqual(request_body["tools"], [{"type": "web_search"}])
        self.assertEqual(output["items"], items)
        self.assertEqual(output["grounding_metadata"]["web_search_calls"][0]["id"], "search_1")

    def test_openai_response_output_text_shortcut_is_accepted(self):
        self.env_path.write_text("OPENAI_API_KEY=openai-key\n", encoding="utf-8")
        items = [
            {"title": f"Item {number}", "url": f"https://example.com/{number}", "summary": "News."}
            for number in range(3)
        ]
        response = json.dumps({"output_text": json.dumps(items)}).encode("utf-8")

        with patch(
            "researcher.urllib.request.urlopen",
            return_value=FakeResponse(response),
        ):
            output = Researcher(
                provider="openai",
                model="gpt-4.1-mini",
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

        self.assertEqual(output["items"], items)

    def test_accepts_research_items_wrapped_in_markdown_code_fence(self):
        items = [
            {"title": f"Item {number}", "url": f"https://example.com/{number}", "summary": "News."}
            for number in range(3)
        ]
        model_text = f"```json\n{json.dumps(items)}\n```"

        with patch(
            "researcher.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response(model_text)),
        ):
            output = Researcher(env_path=self.env_path, prompt_path=self.prompt_path).run()

        self.assertEqual(output["items"], items)
        passed, reason = Researcher.validate(output)
        self.assertTrue(passed, reason)

    def test_accepts_research_items_surrounded_by_explanatory_text(self):
        items = [
            {"title": f"Item {number}", "url": f"https://example.com/{number}", "summary": "News."}
            for number in range(3)
        ]
        model_text = f"Here are the results:\n{json.dumps(items)}\nHope this helps."

        with patch(
            "researcher.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response(model_text)),
        ):
            output = Researcher(env_path=self.env_path, prompt_path=self.prompt_path).run()

        self.assertEqual(output["items"], items)
        passed, reason = Researcher.validate(output)
        self.assertTrue(passed, reason)

    def test_rejects_research_response_without_valid_structured_data(self):
        with patch(
            "researcher.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response("Here are three useful articles.")),
        ):
            with self.assertRaisesRegex(ResearcherError, "Invalid Gemini API search response"):
                Researcher(env_path=self.env_path, prompt_path=self.prompt_path).run()

    def test_rejects_malformed_research_structured_data(self):
        with patch(
            "researcher.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response('[{"title": "A"')),
        ):
            with self.assertRaisesRegex(ResearcherError, "Invalid Gemini API search response"):
                Researcher(env_path=self.env_path, prompt_path=self.prompt_path).run()

    def test_validation_succeeds_for_at_least_three_complete_items(self):
        output = {
            "items": [
                {"title": "A", "url": "https://a.example", "summary": "A summary"},
                {"title": "B", "url": "https://b.example", "summary": "B summary"},
                {"title": "C", "url": "https://c.example", "summary": "C summary"},
            ],
            "grounding_metadata": None,
        }

        passed, reason = Researcher.validate(output)

        self.assertTrue(passed, reason)

    def test_validation_fails_with_fewer_than_three_items(self):
        passed, reason = Researcher.validate({"items": [], "grounding_metadata": None})

        self.assertFalse(passed)
        self.assertIn("fewer than 3", reason)

    def test_validation_fails_when_an_item_lacks_a_required_field(self):
        output = {
            "items": [
                {"title": "A", "url": "https://a.example", "summary": "A summary"},
                {"title": "B", "url": "https://b.example", "summary": "B summary"},
                {"title": "C", "url": "https://c.example"},
            ]
        }

        passed, reason = Researcher.validate(output)

        self.assertFalse(passed)
        self.assertIn("missing", reason)

    def test_gemini_api_errors_are_reported(self):
        with patch(
            "researcher.urllib.request.urlopen",
            side_effect=urllib.error.URLError("service unavailable"),
        ):
            with self.assertRaisesRegex(ResearcherError, "Gemini API search failed"):
                Researcher(env_path=self.env_path, prompt_path=self.prompt_path).run()

    def test_openai_api_errors_are_reported_with_provider_context(self):
        self.env_path.write_text("OPENAI_API_KEY=openai-key\n", encoding="utf-8")

        with patch(
            "researcher.urllib.request.urlopen",
            side_effect=urllib.error.URLError("service unavailable"),
        ):
            with self.assertRaisesRegex(ResearcherError, "OpenAI API search failed"):
                Researcher(
                    provider="openai",
                    model="gpt-4.1-mini",
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run()

    def test_missing_openai_key_reports_readable_failure(self):
        with self.assertRaisesRegex(Exception, "OPENAI_API_KEY"):
            Researcher(
                provider="openai",
                model="gpt-4.1-mini",
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

    def test_unsupported_researcher_provider_reports_readable_failure(self):
        with self.assertRaisesRegex(ResearcherError, "Unsupported Researcher model provider"):
            Researcher(
                provider="other",
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

    def test_missing_prompt_file_reports_failure(self):
        missing_path = Path(self.temporary_directory.name) / "missing.md"

        with self.assertRaisesRegex(ResearcherError, "could not be loaded.*does not exist"):
            Researcher(env_path=self.env_path, prompt_path=missing_path).run()

    def test_unreadable_prompt_file_reports_failure(self):
        with patch("prompt_loader.Path.read_text", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(ResearcherError, "could not be read.*denied"):
                Researcher(env_path=self.env_path, prompt_path=self.prompt_path).run()


if __name__ == "__main__":
    unittest.main()
