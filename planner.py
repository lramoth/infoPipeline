"""Pure-Python coordinator for the infoPipeline stages."""

from __future__ import annotations

import json
import inspect
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from diagnostics import write_diagnostic
from pipeline_config import load_pipeline


ValidationResult = tuple[bool, str]


@dataclass(frozen=True)
class Stage:
    """A named unit of work and the validation applied to its output."""

    name: str
    run: Callable[..., Any]
    validate: Callable[..., ValidationResult]


@dataclass(frozen=True)
class RunResult:
    """The outcome returned to the Planner's caller."""

    succeeded: bool
    output: Any = None
    failed_stage: str | None = None
    reason: str | None = None


class Planner:
    """Run and validate stages sequentially while maintaining a daily ledger."""

    def __init__(
        self,
        stages: Iterable[Any] | None = None,
        ledger_path: str | Path = "output/ledger.json",
    ) -> None:
        self.stages = list(load_pipeline() if stages is None else stages)
        self.ledger_path = Path(ledger_path)

    def run(self) -> RunResult:
        today = date.today().isoformat()
        ledger = self._load_ledger(today)
        previous_output: Any = None

        for index, stage in enumerate(self.stages):
            output: Any = None
            stage_name = self._stage_name(stage)
            stage_input = None if index == 0 else previous_output
            try:
                output = self._run_stage(stage, stage_input, index == 0)
                passed, reason = self._validate_stage(stage, output, stage_input)
            except Exception as error:
                reason = f"{type(error).__name__}: {error}"
                diagnostic_path = self._write_failure_diagnostic(
                    stage_name,
                    error,
                    reason,
                    output=output,
                )
                self._record(ledger, stage_name, "failed", output, reason, diagnostic_path)
                return RunResult(False, output, stage_name, reason)

            status = "done" if passed else "failed"
            diagnostic_path = None
            if not passed:
                diagnostic_path = self._write_validation_diagnostic(
                    stage_name,
                    reason,
                    output,
                )
            self._record(ledger, stage_name, status, output, reason, diagnostic_path)
            if not passed:
                return RunResult(False, output, stage_name, reason)
            previous_output = output

        return RunResult(True, previous_output)

    def _load_ledger(self, today: str) -> dict[str, Any]:
        if self.ledger_path.exists():
            with self.ledger_path.open(encoding="utf-8") as ledger_file:
                ledger = json.load(ledger_file)
            if ledger.get("date") == today:
                return ledger
        return {"date": today, "stages": {}}

    def _record(
        self,
        ledger: dict[str, Any],
        stage_name: str,
        status: str,
        output: Any,
        reason: str,
        diagnostic_path: str | Path | None = None,
    ) -> None:
        entry = {
            "status": status,
            "output": output,
            "validation_reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if diagnostic_path is not None:
            entry["diagnostic_path"] = str(diagnostic_path)
        ledger["stages"][stage_name] = entry
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("w", encoding="utf-8") as ledger_file:
            json.dump(ledger, ledger_file, indent=2)
            ledger_file.write("\n")

    def _write_failure_diagnostic(
        self,
        stage_name: str,
        error: Exception,
        reason: str,
        output: Any,
    ) -> Path | None:
        context = dict(getattr(error, "diagnostic_context", {}) or {})
        failure_category = context.pop("failure_category", "stage_error")
        if output is not None:
            context.setdefault("invalid_stage_output", output)
        return self._try_write_diagnostic(
            stage_name,
            failure_category,
            type(error).__name__,
            reason,
            context,
        )

    def _write_validation_diagnostic(
        self,
        stage_name: str,
        reason: str,
        output: Any,
    ) -> Path | None:
        return self._try_write_diagnostic(
            stage_name,
            "validation_failure",
            "ValidationError",
            reason,
            {
                "validation_reason": reason,
                "invalid_stage_output": output,
            },
        )

    def _try_write_diagnostic(
        self,
        stage_name: str,
        failure_category: str,
        error_type: str,
        error_message: str,
        context: dict[str, Any],
    ) -> Path | None:
        try:
            return write_diagnostic(
                self.ledger_path.parent / "diagnostics",
                stage_name,
                failure_category,
                error_type,
                error_message,
                context,
            )
        except Exception:
            return None

    def _stage_name(self, stage: Any) -> str:
        return getattr(stage, "name", stage.__class__.__name__.lower())

    def _run_stage(self, stage: Any, stage_input: Any, is_first_stage: bool) -> Any:
        run = stage.run
        if is_first_stage or not self._accepts_arguments(run):
            return run()
        return run(stage_input)

    def _validate_stage(
        self,
        stage: Any,
        output: Any,
        stage_input: Any,
    ) -> ValidationResult:
        validate = stage.validate
        if self._accepts_n_arguments(validate, 2):
            return validate(output, stage_input)
        return validate(output)

    def _accepts_arguments(self, function: Callable[..., Any]) -> bool:
        signature = inspect.signature(function)
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                return True
            if parameter.default is inspect.Parameter.empty:
                return True
        return False

    def _accepts_n_arguments(self, function: Callable[..., Any], count: int) -> bool:
        signature = inspect.signature(function)
        positional_parameters = [
            parameter
            for parameter in signature.parameters.values()
            if parameter.kind
            in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        if any(
            parameter.kind == inspect.Parameter.VAR_POSITIONAL
            for parameter in signature.parameters.values()
        ):
            return True
        return len(positional_parameters) >= count


def _format_cli_output(output: Any) -> str:
    if isinstance(output, str):
        return output
    try:
        return json.dumps(output, indent=2)
    except TypeError:
        return str(output)


def main() -> int:
    """Run the default configured pipeline once from the command line."""
    try:
        result = Planner().run()
    except Exception as error:
        print(f"Pipeline failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 1

    if result.succeeded:
        print(_format_cli_output(result.output))
        return 0

    failed_stage = result.failed_stage or "unknown stage"
    reason = result.reason or "no failure reason provided"
    print(f"Pipeline failed at {failed_stage}: {reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
