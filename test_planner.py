import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date, datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from planner import Planner, RunResult, Stage, main


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.ledger_path = Path(self.temporary_directory.name) / "output" / "ledger.json"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def read_ledger(self):
        return json.loads(self.ledger_path.read_text(encoding="utf-8"))

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

        with patch("planner.load_pipeline", return_value=configured_stages) as load_pipeline:
            result = Planner(ledger_path=self.ledger_path).run()

        load_pipeline.assert_called_once_with()
        self.assertTrue(result.succeeded)
        self.assertEqual(result.output, "final output")
        self.assertEqual(
            list(self.read_ledger()["stages"]),
            ["researcher", "writer"],
        )

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
            exit_code = main()

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
            exit_code = main()

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("Pipeline failed at writer: bad format", stderr.getvalue())

    def test_cli_prints_readable_error_and_exits_nonzero_on_startup_error(self):
        stdout = StringIO()
        stderr = StringIO()
        with patch("planner.Planner", side_effect=RuntimeError("missing config")), \
            redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main()

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("Pipeline failed: RuntimeError: missing config", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
