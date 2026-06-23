"""Pure-Python coordinator for the infoPipeline stages."""

from __future__ import annotations

import json
import inspect
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

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
                self._record(ledger, stage_name, "failed", output, reason)
                return RunResult(False, output, stage_name, reason)

            status = "done" if passed else "failed"
            self._record(ledger, stage_name, status, output, reason)
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
    ) -> None:
        ledger["stages"][stage_name] = {
            "status": status,
            "output": output,
            "validation_reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("w", encoding="utf-8") as ledger_file:
            json.dump(ledger, ledger_file, indent=2)
            ledger_file.write("\n")

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
