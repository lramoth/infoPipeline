from __future__ import annotations

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from curator import Curator, CuratorError


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
    return make_api_text_response(json.dumps(curated_items))


def make_api_text_response(model_text: str) -> bytes:
    response = {
        "candidates": [
            {"content": {"parts": [{"text": model_text}]}}
        ]
    }
    return json.dumps(response).encode("utf-8")


def make_openai_response(model_text: str) -> bytes:
    return json.dumps(
        {
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": model_text}],
                }
            ]
        }
    ).encode("utf-8")


class CuratorTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.env_path = Path(self.temporary_directory.name) / ".env"
        self.env_path.write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")
        self.prompt_path = Path(self.temporary_directory.name) / "curator.md"
        self.prompt_path.write_text("custom curator prompt", encoding="utf-8")
        self.gemini_endpoint = "https://gemini.example/v1beta/models"
        self.openai_endpoint = "https://openai.example/responses"

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
            output = Curator(
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run(input_items)

        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://gemini.example/v1beta/models/gemini-2.5-flash:generateContent",
        )
        self.assertEqual(request.headers["X-goog-api-key"], "test-key")
        request_body = json.loads(request.data)
        prompt_text = request_body["contents"][0]["parts"][0]["text"]
        self.assertIn("custom curator prompt", prompt_text)
        self.assertIn(json.dumps(input_items, indent=2), prompt_text)
        self.assertNotIn("tools", request_body)
        self.assertEqual(output, curated)

    def test_sends_items_to_openai_without_search_and_returns_curated_list(self):
        self.env_path.write_text("OPENAI_API_KEY=openai-key\n", encoding="utf-8")
        input_items = [
            {"title": "A", "url": "https://a.example", "summary": "A summary"},
            {"title": "B", "url": "https://b.example", "summary": "B summary"},
        ]
        curated = [make_curated_item(1), make_curated_item(2)]

        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(make_openai_response(json.dumps(curated))),
        ) as urlopen:
            output = Curator(
                provider="openai",
                model="gpt-4.1-mini",
                endpoint=self.openai_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run(input_items)

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, self.openai_endpoint)
        self.assertEqual(request.headers["Authorization"], "Bearer openai-key")
        request_body = json.loads(request.data)
        self.assertEqual(request_body["model"], "gpt-4.1-mini")
        self.assertIn("custom curator prompt", request_body["input"])
        self.assertIn(json.dumps(input_items, indent=2), request_body["input"])
        self.assertNotIn("tools", request_body)
        self.assertEqual(output, curated)

    def test_openai_response_output_text_shortcut_is_accepted(self):
        self.env_path.write_text("OPENAI_API_KEY=openai-key\n", encoding="utf-8")
        curated = [make_curated_item(1)]
        response = json.dumps({"output_text": json.dumps(curated)}).encode("utf-8")

        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(response),
        ):
            output = Curator(
                provider="openai",
                model="gpt-4.1-mini",
                endpoint=self.openai_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run([])

        self.assertEqual(output, curated)

    def test_accepts_curated_items_wrapped_in_markdown_code_fence(self):
        curated = [make_curated_item(1), make_curated_item(2)]
        model_text = f"```json\n{json.dumps(curated)}\n```"

        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(make_api_text_response(model_text)),
        ):
            output = Curator(
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run([])

        self.assertEqual(output, curated)
        passed, reason = Curator.validate(output)
        self.assertTrue(passed, reason)

    def test_accepts_curated_items_surrounded_by_explanatory_text(self):
        curated = [make_curated_item(1), make_curated_item(2)]
        model_text = f"Curated list follows:\n{json.dumps(curated)}\nThese are ranked."

        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(make_api_text_response(model_text)),
        ):
            output = Curator(
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run([])

        self.assertEqual(output, curated)
        passed, reason = Curator.validate(output)
        self.assertTrue(passed, reason)

    def test_rejects_curator_response_without_valid_structured_data(self):
        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(make_api_text_response("A ranked list would go here.")),
        ):
            with self.assertRaisesRegex(CuratorError, "Invalid Gemini API curation response"):
                Curator(
                    endpoint=self.gemini_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run([])

    def test_rejects_malformed_curator_structured_data(self):
        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(make_api_text_response('[{"title": "A"')),
        ):
            with self.assertRaisesRegex(CuratorError, "Invalid Gemini API curation response"):
                Curator(
                    endpoint=self.gemini_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run([])

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

    def test_validation_succeeds_for_multiple_complete_items_sharing_same_url(self):
        shared_url = "https://example.com/same"
        output = [
            make_curated_item(1, url=shared_url),
            make_curated_item(2, url=shared_url),
        ]

        passed, reason = Curator.validate(output)

        self.assertTrue(passed, reason)

    def test_validation_fails_when_item_is_missing_url(self):
        output = [
            {
                "title": "A",
                "summary": "A summary",
                "curation_reason": "Good reason",
                "rank": 1,
            }
        ]

        passed, reason = Curator.validate(output)

        self.assertFalse(passed)
        self.assertIn("missing", reason)

    def test_validation_fails_when_item_has_empty_url(self):
        output = [{**make_curated_item(1), "url": ""}]

        passed, reason = Curator.validate(output)

        self.assertFalse(passed)
        self.assertIn("missing", reason)

    def test_validation_allows_same_domain_with_distinct_complete_urls(self):
        output = [
            make_curated_item(1, url="https://example.com/releases/alpha"),
            make_curated_item(2, url="https://example.com/releases/beta"),
        ]

        passed, reason = Curator.validate(output)

        self.assertTrue(passed, reason)

    def test_validation_allows_same_path_prefix_with_distinct_complete_urls(self):
        output = [
            make_curated_item(1, url="https://news.example.com/items/source?id=alpha"),
            make_curated_item(2, url="https://news.example.com/items/source?id=beta"),
        ]

        passed, reason = Curator.validate(output)

        self.assertTrue(passed, reason)

    def test_validation_allows_distinct_gemini_grounding_redirect_urls(self):
        output = [
            make_curated_item(
                1,
                url="https://vertexaisearch.cloud.google.com/grounding-api-redirect/AWQVqAKLongTokenOne",
            ),
            make_curated_item(
                2,
                url="https://vertexaisearch.cloud.google.com/grounding-api-redirect/AWQVqAKLongTokenTwo",
            ),
        ]

        passed, reason = Curator.validate(output)

        self.assertTrue(passed, reason)

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
                Curator(
                    endpoint=self.gemini_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run([])

    def test_openai_api_errors_are_reported_with_provider_context(self):
        self.env_path.write_text("OPENAI_API_KEY=openai-key\n", encoding="utf-8")

        with patch(
            "curator.urllib.request.urlopen",
            side_effect=urllib.error.URLError("service unavailable"),
        ):
            with self.assertRaisesRegex(CuratorError, "OpenAI API curation failed"):
                Curator(
                    provider="openai",
                    model="gpt-4.1-mini",
                    endpoint=self.openai_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run([])

    def test_missing_openai_key_reports_readable_failure(self):
        with self.assertRaisesRegex(Exception, "OPENAI_API_KEY"):
            Curator(
                provider="openai",
                model="gpt-4.1-mini",
                endpoint=self.openai_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run([])

    def test_unsupported_curator_provider_reports_readable_failure(self):
        with self.assertRaisesRegex(CuratorError, "Unsupported Curator model provider"):
            Curator(
                provider="other",
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run([])

    def test_malformed_gemini_response_raises_curator_error(self):
        bad_response = json.dumps({"candidates": [{"content": {"parts": [{"text": "not json"}]}}]}).encode()

        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(bad_response),
        ):
            with self.assertRaisesRegex(CuratorError, "Invalid Gemini API curation response"):
                Curator(
                    endpoint=self.gemini_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run([])

    def test_loads_configured_prompt_at_run_time(self):
        self.prompt_path.write_text("updated curator prompt", encoding="utf-8")
        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response([make_curated_item(1)])),
        ) as urlopen:
            Curator(
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run([])

        request_body = json.loads(urlopen.call_args.args[0].data)
        self.assertIn("updated curator prompt", request_body["contents"][0]["parts"][0]["text"])

    def test_missing_prompt_file_reports_failure(self):
        missing_path = Path(self.temporary_directory.name) / "missing.md"

        with self.assertRaisesRegex(CuratorError, "could not be loaded.*does not exist"):
            Curator(
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=missing_path,
            ).run([])

    def test_unreadable_prompt_file_reports_failure(self):
        with patch("prompt_loader.Path.read_text", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(CuratorError, "could not be read.*denied"):
                Curator(
                    endpoint=self.gemini_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run([])


if __name__ == "__main__":
    unittest.main()
