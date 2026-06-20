import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from researcher import RESEARCH_PROMPT, Researcher, ResearcherError


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class ResearcherTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.env_path = Path(self.temporary_directory.name) / ".env"
        self.env_path.write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")

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
            output = Researcher(env_path=self.env_path).run()

        request = urlopen.call_args.args[0]
        self.assertEqual(request.headers["X-goog-api-key"], "test-key")
        request_body = json.loads(request.data)
        self.assertEqual(request_body["contents"][0]["parts"][0]["text"], RESEARCH_PROMPT)
        self.assertIn("last 7 days", RESEARCH_PROMPT)
        self.assertEqual(request_body["tools"], [{"google_search": {}}])
        self.assertEqual(output["items"], items)
        self.assertEqual(output["grounding_metadata"], grounding_metadata)

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
                Researcher(env_path=self.env_path).run()


if __name__ == "__main__":
    unittest.main()
