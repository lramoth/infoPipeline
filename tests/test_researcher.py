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


def make_bandcamp_result(
    item_id: int,
    title: str,
    artist: str,
    item_url: str,
) -> dict:
    return {
        "item_id": item_id,
        "item_type": "a",
        "result_type": "a",
        "title": title,
        "item_url": item_url,
        "album_artist": artist,
        "band_name": "Mutual Rytm",
        "band_location": "Stuttgart, Germany",
        "release_date": "2026-06-25 00:00:00 UTC",
        "track_count": 8,
        "featured_track": {"title": "1000 Places"},
        "package_info": [{"format": "vinyl"}],
    }


def make_grounding_metadata(count: int = 3) -> dict:
    return {
        "webSearchQueries": ["recent techno production news"],
        "groundingChunks": [
            {
                "web": {
                    "uri": f"https://grounded.example.com/{number}",
                    "title": f"Source {number}",
                }
            }
            for number in range(count)
        ],
    }


class ResearcherTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.env_path = Path(self.temporary_directory.name) / ".env"
        self.env_path.write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")
        self.prompt_path = Path(self.temporary_directory.name) / "research.md"
        self.prompt_path.write_text("custom research prompt", encoding="utf-8")
        self.gemini_endpoint = "https://gemini.example/v1beta/models"
        self.openai_endpoint = "https://openai.example/responses"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_searches_gemini_and_records_compact_provider_context(self):
        items = [
            {"title": f"Item {number}", "summary": "News."}
            for number in range(3)
        ]
        grounding_metadata = make_grounding_metadata()
        response = {
            "candidates": [
                {
                    "content": {"parts": [{"text": json.dumps(items)}]},
                    "groundingMetadata": grounding_metadata,
                }
            ]
        }

        with patch(
            "researcher_providers.gemini.urllib.request.urlopen",
            return_value=FakeResponse(json.dumps(response).encode("utf-8")),
        ) as urlopen:
            output = Researcher(
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://gemini.example/v1beta/models/gemini-2.5-flash:generateContent",
        )
        self.assertEqual(request.headers["X-goog-api-key"], "test-key")
        request_body = json.loads(request.data)
        self.assertEqual(request_body["contents"][0]["parts"][0]["text"], "custom research prompt")
        self.assertEqual(request_body["tools"], [{"google_search": {}}])
        self.assertEqual(
            output["items"],
            [
                {
                    "title": f"Item {number}",
                    "url": f"https://grounded.example.com/{number}",
                    "summary": "News.",
                }
                for number in range(3)
            ],
        )
        self.assertNotIn("grounding_metadata", output)
        self.assertEqual(output["raw_provider_response"]["provider"], "Gemini")
        self.assertIn("groundingChunks", output["raw_provider_response"]["response_preview"])
        self.assertEqual(
            output["raw_provider_response"]["search_context"]["groundingChunks"][0]["uri"],
            "https://grounded.example.com/0",
        )
        self.assertEqual(
            output["normalization"]["url_source"],
            "provider_grounding_metadata",
        )

    def test_searches_openai_with_web_search_and_returns_existing_output_contract(self):
        self.env_path.write_text("OPENAI_API_KEY=openai-key\n", encoding="utf-8")
        items = [
            {"title": f"Item {number}", "url": f"https://example.com/{number}", "summary": "News."}
            for number in range(3)
        ]

        with patch(
            "researcher_providers.openai.urllib.request.urlopen",
            return_value=FakeResponse(make_openai_response(json.dumps(items))),
        ) as urlopen:
            output = Researcher(
                provider="openai",
                model="gpt-4.1-mini",
                endpoint=self.openai_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, self.openai_endpoint)
        self.assertEqual(request.headers["Authorization"], "Bearer openai-key")
        request_body = json.loads(request.data)
        self.assertEqual(request_body["model"], "gpt-4.1-mini")
        self.assertEqual(request_body["input"], "custom research prompt")
        self.assertEqual(request_body["tools"], [{"type": "web_search"}])
        self.assertEqual(request_body["tool_choice"], "required")
        self.assertEqual(request_body["include"], ["web_search_call.action.sources"])
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
            "researcher_providers.openai.urllib.request.urlopen",
            return_value=FakeResponse(response),
        ):
            output = Researcher(
                provider="openai",
                model="gpt-4.1-mini",
                endpoint=self.openai_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

        self.assertEqual(output["items"], items)

    def test_searches_bandcamp_without_prompt_and_returns_existing_output_contract(self):
        response = {
            "results": [
                make_bandcamp_result(
                    1,
                    "Planets and Stars",
                    "Dextro",
                    "https://mutual-rytm.bandcamp.com/album/planets-and-stars?from=discover_page",
                ),
                make_bandcamp_result(
                    2,
                    "Nightrun",
                    "Disguised",
                    "https://mutual-rytm.bandcamp.com/album/nightrun?from=discover_page",
                ),
                make_bandcamp_result(
                    3,
                    "TECH041",
                    "Nastia",
                    "https://example.bandcamp.com/album/tech041?from=discover_page",
                ),
            ]
        }

        with patch(
            "researcher_providers.bandcamp.urllib.request.urlopen",
            return_value=FakeResponse(json.dumps(response).encode("utf-8")),
        ) as urlopen:
            output = Researcher(provider="bandcamp").run()

        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://bandcamp.com/api/discover/1/discover_web",
        )
        request_body = json.loads(request.data)
        self.assertEqual(request_body["tag_norm_names"], ["hypnotic-techno", "techno"])
        self.assertEqual(request_body["slice"], "new")
        self.assertEqual(request_body["time_facet_id"], 0)
        self.assertEqual(output["items"][0]["title"], "Dextro - Planets and Stars")
        self.assertEqual(
            output["items"][0]["url"],
            "https://mutual-rytm.bandcamp.com/album/planets-and-stars",
        )
        self.assertIn("2026-06-25 Bandcamp release", output["items"][0]["summary"])
        self.assertIn("with 8 tracks", output["items"][0]["summary"])
        self.assertEqual(output["raw_provider_response"]["provider"], "Bandcamp")
        passed, reason = Researcher.validate(output)
        self.assertTrue(passed, reason)

    def test_bandcamp_uses_configured_discovery_criteria(self):
        response = {
            "results": [
                make_bandcamp_result(
                    1,
                    "Dub Signals",
                    "Filtered",
                    "https://filtered.bandcamp.com/album/dub-signals?from=discover_page",
                ),
                make_bandcamp_result(
                    2,
                    "Night Current",
                    "Signal Phase",
                    "https://signal-phase.bandcamp.com/album/night-current?from=discover_page",
                ),
                make_bandcamp_result(
                    3,
                    "Low Ceiling",
                    "North Loop",
                    "https://north-loop.bandcamp.com/album/low-ceiling?from=discover_page",
                ),
            ]
        }
        discovery = {
            "category_id": 0,
            "tag_norm_names": ["dub-techno"],
            "geoname_id": 123,
            "slice": "top",
            "time_facet_id": 7,
            "cursor": "abc",
            "size": 12,
            "include_result_types": ["a"],
        }

        with patch(
            "researcher_providers.bandcamp.urllib.request.urlopen",
            return_value=FakeResponse(json.dumps(response).encode("utf-8")),
        ) as urlopen:
            output = Researcher(provider="bandcamp", discovery=discovery).run()

        request = urlopen.call_args.args[0]
        self.assertEqual(json.loads(request.data), discovery)
        self.assertEqual(output["raw_provider_response"]["request_body"], discovery)
        passed, reason = Researcher.validate(output)
        self.assertTrue(passed, reason)

    def test_bandcamp_malformed_response_reports_readable_failure(self):
        with patch(
            "researcher_providers.bandcamp.urllib.request.urlopen",
            return_value=FakeResponse(json.dumps({"items": []}).encode("utf-8")),
        ):
            with self.assertRaisesRegex(
                ResearcherError,
                "Bandcamp Discover response was malformed",
            ):
                Researcher(provider="bandcamp").run()

    def test_bandcamp_response_with_fewer_than_three_items_fails_validation(self):
        response = {
            "results": [
                make_bandcamp_result(
                    1,
                    "Planets and Stars",
                    "Dextro",
                    "https://mutual-rytm.bandcamp.com/album/planets-and-stars?from=discover_page",
                ),
                {"title": "Missing URL", "album_artist": "Artist"},
            ]
        }

        with patch(
            "researcher_providers.bandcamp.urllib.request.urlopen",
            return_value=FakeResponse(json.dumps(response).encode("utf-8")),
        ):
            output = Researcher(provider="bandcamp").run()

        passed, reason = Researcher.validate(output)
        self.assertFalse(passed)
        self.assertIn("fewer than 3", reason)

    def test_accepts_research_items_wrapped_in_markdown_code_fence(self):
        items = [
            {"title": f"Item {number}", "summary": "News."}
            for number in range(3)
        ]
        model_text = f"```json\n{json.dumps(items)}\n```"
        grounding_metadata = make_grounding_metadata()

        with patch(
            "researcher_providers.gemini.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response(model_text, grounding_metadata)),
        ):
            output = Researcher(
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

        self.assertEqual(output["items"][0]["url"], "https://grounded.example.com/0")
        passed, reason = Researcher.validate(output)
        self.assertTrue(passed, reason)

    def test_accepts_research_items_surrounded_by_explanatory_text(self):
        items = [
            {"title": f"Item {number}", "summary": "News."}
            for number in range(3)
        ]
        model_text = f"Here are the results:\n{json.dumps(items)}\nHope this helps."
        grounding_metadata = make_grounding_metadata()

        with patch(
            "researcher_providers.gemini.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response(model_text, grounding_metadata)),
        ):
            output = Researcher(
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

        self.assertEqual(output["items"][1]["url"], "https://grounded.example.com/1")
        passed, reason = Researcher.validate(output)
        self.assertTrue(passed, reason)

    def test_accepts_line_based_gemini_research_items_and_normalizes_to_json(self):
        model_text = """
ITEM 1
Title: First story
Summary: First summary.

ITEM 2
Title: Second story
Summary: Second summary.

ITEM 3
Title: Third story
Summary: Third summary.
"""

        with patch(
            "researcher_providers.gemini.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response(model_text, make_grounding_metadata())),
        ):
            output = Researcher(
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

        self.assertEqual(
            output["items"],
            [
                {
                    "title": "First story",
                    "url": "https://grounded.example.com/0",
                    "summary": "First summary.",
                },
                {
                    "title": "Second story",
                    "url": "https://grounded.example.com/1",
                    "summary": "Second summary.",
                },
                {
                    "title": "Third story",
                    "url": "https://grounded.example.com/2",
                    "summary": "Third summary.",
                },
            ],
        )

    def test_rejects_research_response_without_valid_structured_data(self):
        with patch(
            "researcher_providers.gemini.urllib.request.urlopen",
            return_value=FakeResponse(
                make_api_response("Here are three useful articles.", make_grounding_metadata())
            ),
        ):
            with self.assertRaisesRegex(
                ResearcherError,
                "could not create normalized research items",
            ):
                Researcher(
                    endpoint=self.gemini_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run()

    def test_rejects_malformed_research_structured_data(self):
        with patch(
            "researcher_providers.gemini.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response('[{"title": "A"', make_grounding_metadata())),
        ):
            with self.assertRaisesRegex(
                ResearcherError,
                "could not create normalized research items",
            ):
                Researcher(
                    endpoint=self.gemini_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run()

    def test_rejects_gemini_response_without_source_context(self):
        items = [
            {"title": f"Item {number}", "summary": "News."}
            for number in range(3)
        ]

        with patch(
            "researcher_providers.gemini.urllib.request.urlopen",
            return_value=FakeResponse(make_api_response(json.dumps(items))),
        ):
            with self.assertRaisesRegex(
                ResearcherError,
                "no usable search source context",
            ) as error:
                Researcher(
                    endpoint=self.gemini_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run()

        self.assertEqual(
            error.exception.diagnostic_context["failure_category"],
            "provider_source_context_missing",
        )

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

    def test_openai_zero_item_response_reports_provider_context(self):
        self.env_path.write_text("OPENAI_API_KEY=openai-key\n", encoding="utf-8")

        with patch(
            "researcher_providers.openai.urllib.request.urlopen",
            return_value=FakeResponse(make_openai_response("[]")),
        ):
            with self.assertRaisesRegex(ResearcherError, "OpenAI API search produced no research items") as error:
                Researcher(
                    provider="openai",
                    model="gpt-4.1-mini",
                    endpoint=self.openai_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run()

        context = error.exception.diagnostic_context
        self.assertEqual(context["failure_category"], "model_output_empty")
        self.assertEqual(context["provider_name"], "OpenAI")
        self.assertEqual(context["model_name"], "gpt-4.1-mini")
        self.assertEqual(context["raw_model_text_preview"], "[]")
        self.assertEqual(context["provider_search_context_preview"]["web_search_calls"][0]["id"], "search_1")

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
            "researcher_providers.gemini.urllib.request.urlopen",
            side_effect=urllib.error.URLError("service unavailable"),
        ):
            with self.assertRaisesRegex(ResearcherError, "Gemini API search failed"):
                Researcher(
                    endpoint=self.gemini_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run()

    def test_openai_api_errors_are_reported_with_provider_context(self):
        self.env_path.write_text("OPENAI_API_KEY=openai-key\n", encoding="utf-8")

        with patch(
            "researcher_providers.openai.urllib.request.urlopen",
            side_effect=urllib.error.URLError("service unavailable"),
        ):
            with self.assertRaisesRegex(ResearcherError, "OpenAI API search failed"):
                Researcher(
                    provider="openai",
                    model="gpt-4.1-mini",
                    endpoint=self.openai_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run()

    def test_missing_openai_key_reports_readable_failure(self):
        with self.assertRaisesRegex(Exception, "OPENAI_API_KEY"):
            Researcher(
                provider="openai",
                model="gpt-4.1-mini",
                endpoint=self.openai_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

    def test_unsupported_researcher_provider_reports_readable_failure(self):
        with self.assertRaisesRegex(ResearcherError, "Unsupported Researcher provider"):
            Researcher(
                provider="other",
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=self.prompt_path,
            ).run()

    def test_missing_prompt_file_reports_failure(self):
        missing_path = Path(self.temporary_directory.name) / "missing.md"

        with self.assertRaisesRegex(ResearcherError, "could not be loaded.*does not exist"):
            Researcher(
                endpoint=self.gemini_endpoint,
                env_path=self.env_path,
                prompt_path=missing_path,
            ).run()

    def test_unreadable_prompt_file_reports_failure(self):
        with patch("prompt_loader.Path.read_text", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(ResearcherError, "could not be read.*denied"):
                Researcher(
                    endpoint=self.gemini_endpoint,
                    env_path=self.env_path,
                    prompt_path=self.prompt_path,
                ).run()


if __name__ == "__main__":
    unittest.main()
