import io
import json
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from datetime import date, datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from curator import Curator
from delivery import DeliveryResult
from planner import Planner, RunResult, Stage, main
from writer import Writer


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class FakeDelivery:
    name = "telegram"

    def __init__(self, events=None, result=None, error=None):
        self.events = events if events is not None else []
        self.result = result or DeliveryResult("telegram", True, "sent")
        self.error = error

    def deliver(self, message):
        self.events.append(("delivery", message))
        if self.error is not None:
            raise self.error
        return self.result


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.ledger_path = Path(self.temporary_directory.name) / "output" / "ledger.json"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def read_ledger(self):
        return json.loads(self.ledger_path.read_text(encoding="utf-8"))

    def read_diagnostic(self, stage_name):
        diagnostic_path = Path(self.read_ledger()["stages"][stage_name]["diagnostic_path"])
        return json.loads(diagnostic_path.read_text(encoding="utf-8"))

    def test_runs_and_validates_stages_in_order(self):
        events = []

        def first_run():
            events.append("run first")
            return {"item": 1}

        def first_validate(output):
            events.append("validate first")
            return True, "first passed"

        def second_run():
            self.assertIn("first", self.read_ledger()["stages"])
            events.append("run second")
            return "second output"

        def second_validate(output):
            events.append("validate second")
            return True, "second passed"

        result = Planner(
            [
                Stage("first", first_run, first_validate),
                Stage("second", second_run, second_validate),
            ],
            self.ledger_path,
        ).run()

        self.assertTrue(result.succeeded)
        self.assertEqual(
            events,
            ["run first", "validate first", "run second", "validate second"],
        )
        ledger = self.read_ledger()
        self.assertEqual(ledger["date"], date.today().isoformat())
        self.assertEqual(ledger["stages"]["first"]["status"], "done")
        self.assertEqual(ledger["stages"]["second"]["status"], "done")
        self.assertNotIn("diagnostic_path", ledger["stages"]["first"])
        self.assertFalse((self.ledger_path.parent / "diagnostics").exists())
        self.assertEqual(ledger["stages"]["first"]["output"], {"item": 1})
        self.assertEqual(result.output, "second output")
        self.assertEqual(
            ledger["stages"]["first"]["validation_reason"], "first passed"
        )
        datetime.fromisoformat(ledger["stages"]["first"]["timestamp"])

    def test_passes_each_successful_stage_output_to_the_next_stage(self):
        events = []

        def first_run():
            events.append(("first input", None))
            return {"items": [1, 2, 3]}

        def second_run(previous_output):
            events.append(("second input", previous_output))
            return {"curated": previous_output["items"]}

        def third_run(previous_output):
            events.append(("third input", previous_output))
            return "final message"

        result = Planner(
            [
                Stage("researcher", first_run, lambda output: (True, "research passed")),
                Stage("curator", second_run, lambda output: (True, "curation passed")),
                Stage("writer", third_run, lambda output: (True, "writer passed")),
            ],
            self.ledger_path,
        ).run()

        self.assertTrue(result.succeeded)
        self.assertEqual(result.output, "final message")
        self.assertEqual(
            events,
            [
                ("first input", None),
                ("second input", {"items": [1, 2, 3]}),
                ("third input", {"curated": [1, 2, 3]}),
            ],
        )

    def test_delivery_runs_after_writer_success_with_writer_output(self):
        events = []

        result = Planner(
            [
                Stage("researcher", lambda: "research", lambda output: (True, "passed")),
                Stage("writer", lambda output: "final message", lambda output: (True, "passed")),
            ],
            self.ledger_path,
            delivery_providers=[FakeDelivery(events)],
        ).run()

        self.assertTrue(result.succeeded)
        self.assertEqual(result.output, "final message")
        self.assertEqual(events, [("delivery", "final message")])
        ledger = self.read_ledger()
        self.assertEqual(ledger["stages"]["writer"]["output"], "final message")
        self.assertEqual(ledger["delivery"]["telegram"]["provider"], "telegram")
        self.assertEqual(ledger["delivery"]["telegram"]["status"], "done")
        self.assertEqual(ledger["delivery"]["telegram"]["reason"], "sent")
        self.assertNotIn("telegram", ledger["stages"])

    def test_delivery_does_not_run_when_stage_fails(self):
        events = []

        result = Planner(
            [
                Stage("bad", lambda: "bad output", lambda output: (False, "failed")),
                Stage("writer", lambda output: "final message", lambda output: (True, "passed")),
            ],
            self.ledger_path,
            delivery_providers=[FakeDelivery(events)],
        ).run()

        self.assertFalse(result.succeeded)
        self.assertEqual(result.failed_stage, "bad")
        self.assertEqual(events, [])
        self.assertNotIn("delivery", self.read_ledger())

    def test_disabled_delivery_providers_do_not_run(self):
        events = []

        result = Planner(
            [
                Stage("writer", lambda: "final message", lambda output: (True, "passed")),
            ],
            self.ledger_path,
            delivery_providers=[],
        ).run()

        self.assertTrue(result.succeeded)
        self.assertEqual(result.output, "final message")
        self.assertEqual(events, [])
        self.assertNotIn("delivery", self.read_ledger())

    def test_delivery_failure_is_reported_without_failing_writer_stage(self):
        result = Planner(
            [
                Stage("writer", lambda: "final message", lambda output: (True, "passed")),
            ],
            self.ledger_path,
            delivery_providers=[FakeDelivery(error=RuntimeError("network down"))],
        ).run()

        self.assertFalse(result.succeeded)
        self.assertEqual(result.output, "final message")
        self.assertEqual(result.failed_delivery, "telegram")
        self.assertIn("network down", result.reason)
        ledger = self.read_ledger()
        self.assertEqual(ledger["stages"]["writer"]["status"], "done")
        self.assertEqual(ledger["stages"]["writer"]["output"], "final message")
        self.assertEqual(ledger["delivery"]["telegram"]["status"], "failed")
        self.assertIn("network down", ledger["delivery"]["telegram"]["reason"])

    def test_validation_can_use_the_input_given_to_the_current_stage(self):
        validator_seen_input = None

        def validate(output, stage_input):
            nonlocal validator_seen_input
            validator_seen_input = stage_input
            return True, "writer saw curated items"

        result = Planner(
            [
                Stage("curator", lambda: [{"rank": 1}], lambda output: (True, "passed")),
                Stage("writer", lambda items: "message", validate),
            ],
            self.ledger_path,
        ).run()

        self.assertTrue(result.succeeded)
        self.assertEqual(validator_seen_input, [{"rank": 1}])

    def test_loads_default_stages_from_pipeline_config_when_stages_are_not_given(self):
        configured_stages = [
            Stage("researcher", lambda: "research output", lambda output: (True, "research passed")),
            Stage("writer", lambda output: "final output", lambda output: (True, "writer passed")),
        ]

        with patch("planner.load_pipeline", return_value=configured_stages) as load_pipeline, \
            patch("planner.load_delivery_config", return_value=[]) as load_delivery_config:
            result = Planner(ledger_path=self.ledger_path).run()

        load_pipeline.assert_called_once_with("techno")
        load_delivery_config.assert_called_once_with()
        self.assertTrue(result.succeeded)
        self.assertEqual(result.output, "final output")
        self.assertEqual(
            list(self.read_ledger()["stages"]),
            ["researcher", "writer"],
        )

    def test_default_config_uses_profile_specific_ledger_and_records_profile(self):
        configured_stages = [
            Stage("writer", lambda: "profile output", lambda output: (True, "passed")),
        ]
        profile_ledger = Path(self.temporary_directory.name) / "output" / "finance" / "ledger.json"

        with patch("planner.resolve_profile_name", return_value="finance"), \
            patch("planner.load_pipeline", return_value=configured_stages), \
            patch("planner.load_delivery_config", return_value=[]), \
            patch("planner.profile_ledger_path", return_value=profile_ledger):
            result = Planner(profile_name="finance").run()

        self.assertTrue(result.succeeded)
        ledger = json.loads(profile_ledger.read_text(encoding="utf-8"))
        self.assertEqual(ledger["profile"], "finance")
        self.assertEqual(ledger["stages"]["writer"]["status"], "done")

    def test_invalid_stage_is_reported_and_halts_remaining_stages(self):
        ran_last_stage = False

        def last_run():
            nonlocal ran_last_stage
            ran_last_stage = True

        result = Planner(
            [
                Stage("bad", lambda: "bad output", lambda output: (False, "off taste")),
                Stage("last", last_run, lambda output: (True, "passed")),
            ],
            self.ledger_path,
        ).run()

        self.assertFalse(result.succeeded)
        self.assertEqual(result.failed_stage, "bad")
        self.assertEqual(result.reason, "off taste")
        self.assertFalse(ran_last_stage)
        ledger = self.read_ledger()
        self.assertEqual(ledger["stages"]["bad"]["status"], "failed")
        diagnostic = self.read_diagnostic("bad")
        self.assertEqual(diagnostic["stage_name"], "bad")
        self.assertEqual(diagnostic["failure_category"], "validation_failure")
        self.assertEqual(diagnostic["error_type"], "ValidationError")
        self.assertEqual(diagnostic["validation_reason"], "off taste")
        self.assertEqual(diagnostic["invalid_stage_output_preview"], "bad output")
        self.assertNotIn("last", ledger["stages"])

    def test_starts_fresh_ledger_when_saved_date_is_not_today(self):
        self.ledger_path.parent.mkdir(parents=True)
        old_date = (date.today() - timedelta(days=1)).isoformat()
        self.ledger_path.write_text(
            json.dumps({"date": old_date, "stages": {"old": {"status": "done"}}}),
            encoding="utf-8",
        )

        Planner(
            [Stage("new", lambda: 1, lambda output: (True, "passed"))],
            self.ledger_path,
        ).run()

        ledger = self.read_ledger()
        self.assertEqual(ledger["date"], date.today().isoformat())
        self.assertNotIn("old", ledger["stages"])
        self.assertIn("new", ledger["stages"])

    def test_reuses_todays_ledger_and_overwrites_rerun_stage(self):
        self.ledger_path.parent.mkdir(parents=True)
        self.ledger_path.write_text(
            json.dumps(
                {
                    "date": date.today().isoformat(),
                    "stages": {
                        "keep": {"status": "done"},
                        "rerun": {"status": "failed", "output": "old"},
                    },
                }
            ),
            encoding="utf-8",
        )

        Planner(
            [Stage("rerun", lambda: "new", lambda output: (True, "now valid"))],
            self.ledger_path,
        ).run()

        ledger = self.read_ledger()
        self.assertIn("keep", ledger["stages"])
        self.assertEqual(ledger["stages"]["rerun"]["status"], "done")
        self.assertEqual(ledger["stages"]["rerun"]["output"], "new")

    def test_run_error_fails_stage_and_halts(self):
        ran_last_stage = False

        def raise_error():
            raise RuntimeError("service unavailable")

        def last_run():
            nonlocal ran_last_stage
            ran_last_stage = True

        result = Planner(
            [
                Stage("broken", raise_error, lambda output: (True, "passed")),
                Stage("last", last_run, lambda output: (True, "passed")),
            ],
            self.ledger_path,
        ).run()

        self.assertFalse(result.succeeded)
        self.assertEqual(result.failed_stage, "broken")
        self.assertIn("service unavailable", result.reason)
        self.assertFalse(ran_last_stage)
        entry = self.read_ledger()["stages"]["broken"]
        self.assertEqual(entry["status"], "failed")
        self.assertIsNone(entry["output"])
        self.assertIn("service unavailable", entry["validation_reason"])

    def test_curator_json_parse_failure_records_raw_model_text_preview(self):
        env_path = Path(self.temporary_directory.name) / ".env"
        env_path.write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")
        prompt_path = Path(self.temporary_directory.name) / "curator.md"
        prompt_path.write_text("curate", encoding="utf-8")
        response = {
            "candidates": [
                {"content": {"parts": [{"text": "not json from model"}]}}
            ]
        }

        with patch(
            "curator.urllib.request.urlopen",
            return_value=FakeResponse(json.dumps(response).encode("utf-8")),
        ):
            result = Planner(
                [
                    Stage("researcher", lambda: [], lambda output: (True, "passed")),
                    Curator(env_path=env_path, prompt_path=prompt_path),
                ],
                self.ledger_path,
            ).run()

        self.assertFalse(result.succeeded)
        diagnostic = self.read_diagnostic("curator")
        self.assertEqual(diagnostic["failure_category"], "model_output_parse")
        self.assertEqual(diagnostic["provider_name"], "Gemini")
        self.assertEqual(diagnostic["raw_model_text_preview"], "not json from model")
        self.assertIn("Expecting value", diagnostic["parse_error_message"])

    def test_gemini_api_failure_records_http_context_without_api_key(self):
        env_path = Path(self.temporary_directory.name) / ".env"
        env_path.write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")
        prompt_path = Path(self.temporary_directory.name) / "curator.md"
        prompt_path.write_text("curate", encoding="utf-8")
        error = urllib.error.HTTPError(
            "https://generativelanguage.googleapis.com/failure",
            503,
            "Service Unavailable",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"temporarily unavailable","api_key":"test-key"}'),
        )

        with patch("curator.urllib.request.urlopen", side_effect=error):
            result = Planner(
                [
                    Stage("researcher", lambda: [], lambda output: (True, "passed")),
                    Curator(env_path=env_path, prompt_path=prompt_path),
                ],
                self.ledger_path,
            ).run()

        self.assertFalse(result.succeeded)
        diagnostic = self.read_diagnostic("curator")
        self.assertEqual(diagnostic["failure_category"], "external_http_call")
        self.assertEqual(diagnostic["provider_name"], "Gemini")
        self.assertEqual(diagnostic["model_name"], "gemini-2.5-flash")
        self.assertIn(":generateContent", diagnostic["endpoint_url"])
        self.assertEqual(diagnostic["http_method"], "POST")
        self.assertEqual(diagnostic["response_status"], 503)
        diagnostic_text = json.dumps(diagnostic)
        self.assertIn("temporarily unavailable", diagnostic_text)
        self.assertNotIn("test-key", diagnostic_text)
        self.assertNotIn("X-goog-api-key", diagnostic_text)

    def test_ollama_failure_records_local_endpoint_and_error_message(self):
        prompt_path = Path(self.temporary_directory.name) / "writer.md"
        prompt_path.write_text("write", encoding="utf-8")
        template_path = Path(self.temporary_directory.name) / "template.md"
        template_path.write_text(
            "\n".join(
                [
                    "{items}",
                    "# Item Template",
                    "{title}",
                    "{note}",
                    "{url}",
                ]
            ),
            encoding="utf-8",
        )

        with patch(
            "writer.urllib.request.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            result = Planner(
                [
                    Stage("curator", lambda: [{"title": "A", "url": "https://a.example", "summary": "s", "curation_reason": "r", "rank": 1}], lambda output: (True, "passed")),
                    Writer(prompt_path=prompt_path, template_path=template_path),
                ],
                self.ledger_path,
            ).run()

        self.assertFalse(result.succeeded)
        diagnostic = self.read_diagnostic("writer")
        self.assertEqual(diagnostic["provider_name"], "Ollama")
        self.assertEqual(diagnostic["model_name"], "gemma4:e4b")
        self.assertEqual(diagnostic["endpoint_url"], "http://localhost:11434/api/generate")
        self.assertIn("connection refused", diagnostic["error_message"])

    def test_diagnostic_write_failure_does_not_obscure_original_error(self):
        with patch("planner.write_diagnostic", side_effect=OSError("disk full")):
            result = Planner(
                [Stage("bad", lambda: "bad output", lambda output: (False, "off taste"))],
                self.ledger_path,
            ).run()

        self.assertFalse(result.succeeded)
        self.assertEqual(result.failed_stage, "bad")
        self.assertEqual(result.reason, "off taste")
        entry = self.read_ledger()["stages"]["bad"]
        self.assertEqual(entry["status"], "failed")
        self.assertNotIn("diagnostic_path", entry)

    def test_validation_error_fails_stage_and_records_output(self):
        def raise_error(output):
            raise ValueError("cannot validate")

        result = Planner(
            [Stage("broken validation", lambda: [1, 2], raise_error)],
            self.ledger_path,
        ).run()

        self.assertFalse(result.succeeded)
        self.assertEqual(result.failed_stage, "broken validation")
        entry = self.read_ledger()["stages"]["broken validation"]
        self.assertEqual(entry["status"], "failed")
        self.assertEqual(entry["output"], [1, 2])
        self.assertIn("cannot validate", entry["validation_reason"])

    def test_cli_prints_final_output_and_exits_zero_on_success(self):
        stdout = StringIO()
        stderr = StringIO()
        with patch.object(
            Planner,
            "run",
            return_value=RunResult(True, "final message"),
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main([])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "final message\n")
        self.assertEqual(stderr.getvalue(), "")

    def test_cli_prints_readable_error_and_exits_nonzero_on_run_failure(self):
        stdout = StringIO()
        stderr = StringIO()
        with patch.object(
            Planner,
            "run",
            return_value=RunResult(False, failed_stage="writer", reason="bad format"),
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("Pipeline failed at writer: bad format", stderr.getvalue())

    def test_cli_reports_delivery_failure_separately_from_stage_failure(self):
        stdout = StringIO()
        stderr = StringIO()
        with patch.object(
            Planner,
            "run",
            return_value=RunResult(
                False,
                "final message",
                failed_delivery="telegram",
                reason="network down",
            ),
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "final message\n")
        self.assertIn("Delivery failed for telegram: network down", stderr.getvalue())

    def test_cli_prints_readable_error_and_exits_nonzero_on_startup_error(self):
        stdout = StringIO()
        stderr = StringIO()
        with patch("planner.Planner", side_effect=RuntimeError("missing config")), \
            redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("Pipeline failed: RuntimeError: missing config", stderr.getvalue())

    def test_cli_passes_profile_to_planner(self):
        stdout = StringIO()
        stderr = StringIO()
        with patch("planner.Planner") as planner_class, \
            redirect_stdout(stdout), redirect_stderr(stderr):
            planner_class.return_value.run.return_value = RunResult(True, "profile message")
            exit_code = main(["--profile", "finance"])

        planner_class.assert_called_once_with(profile_name="finance")
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "profile message\n")
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
