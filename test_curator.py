from __future__ import annotations

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from curator import CURATION_PROMPT, Curator, CuratorError


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def make_curated_item(rank: int, url: str | None = None) -> dict:
    return {
        "title": f"Item {rank}",
        "url": url or f"https://example.com/{rank}",
        "summary": f"Summary {rank}.",
        "curation_reason": f"Reason {rank}.",
        "rank": rank,
    }


def make_api_response(curated_items: list) -> bytes:
    response = {
        "candidates": [
            {"content": {"parts": [{"text": json.dumps(curated_items)}]}}
        ]
    }
    return json.dumps(response).encode("utf-8")


class CuratorTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.env_path = Path(self.temporary_directory.name) / ".env"
        self.env_path.write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_sends_items_to_gemini_without_search_and_returns_curated_list(self):
        input_items = [
            {"title": "A", "url": "https://a.example", "summary": "A summary"},
            {"title": "B", "url": "https://b.example", "summary": "B summary"},
        ]
        curated = [make_curated_item(1), make_curated_item(2)]

        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response(curated)),
        ) as urlopen:
            output = Curator(env_path=self.env_path).run(input_items)

        request = urlopen.call_args.args[0]
        self.assertEqual(request.headers["X-goog-api-key"], "test-key")
        request_body = json.loads(request.data)
        prompt_text = request_body["contents"][0]["parts"][0]["text"]
        self.assertIn(CURATION_PROMPT, prompt_text)
        self.assertIn(json.dumps(input_items, indent=2), prompt_text)
        self.assertNotIn("tools", request_body)
        self.assertEqual(output, curated)

    def test_validation_succeeds_for_one_complete_curated_item(self):
        output = [make_curated_item(1)]

        passed, reason = Curator.validate(output)

        self.assertTrue(passed, reason)

    def test_validation_succeeds_for_multiple_complete_items(self):
        output = [make_curated_item(1), make_curated_item(2), make_curated_item(3)]

        passed, reason = Curator.validate(output)

        self.assertTrue(passed, reason)

    def test_validation_fails_when_output_is_empty(self):
        passed, reason = Curator.validate([])

        self.assertFalse(passed)
        self.assertIn("no items", reason)

    def test_validation_fails_when_item_is_missing_curation_reason(self):
        output = [
            {
                "title": "A",
                "url": "https://a.example",
                "summary": "A summary",
                "rank": 1,
            }
        ]

        passed, reason = Curator.validate(output)

        self.assertFalse(passed)
        self.assertIn("missing", reason)

    def test_validation_fails_when_item_is_missing_rank(self):
        output = [
            {
                "title": "A",
                "url": "https://a.example",
                "summary": "A summary",
                "curation_reason": "Good reason",
            }
        ]

        passed, reason = Curator.validate(output)

        self.assertFalse(passed)
        self.assertIn("missing", reason)

    def test_validation_fails_for_duplicate_urls(self):
        shared_url = "https://example.com/same"
        output = [
            make_curated_item(1, url=shared_url),
            make_curated_item(2, url=shared_url),
        ]

        passed, reason = Curator.validate(output)

        self.assertFalse(passed)
        self.assertIn("duplicate", reason)

    def test_validation_fails_when_no_item_has_rank_one(self):
        output = [{**make_curated_item(1), "rank": 2}]

        passed, reason = Curator.validate(output)

        self.assertFalse(passed)
        self.assertIn("rank 1", reason)

    def test_gemini_api_errors_are_reported(self):
        with patch(
            "curator.urllib.request.urlopen",
            side_effect=urllib.error.URLError("service unavailable"),
        ):
            with self.assertRaisesRegex(CuratorError, "Gemini API curation failed"):
                Curator(env_path=self.env_path).run([])

    def test_malformed_gemini_response_raises_curator_error(self):
        bad_response = json.dumps({"candidates": [{"content": {"parts": [{"text": "not json"}]}}]}).encode()

        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(bad_response),
        ):
            with self.assertRaisesRegex(CuratorError, "Invalid Gemini API curation response"):
                Curator(env_path=self.env_path).run([])


if __name__ == "__main__":
    unittest.main()
