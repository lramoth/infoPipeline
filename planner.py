"""Pure-Python coordinator for the infoPipeline stages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


ValidationResult = tuple[bool, str]


@dataclass(frozen=True)
class Stage:
    """A named unit of work and the validation applied to its output."""

    name: str
    run: Callable[[], Any]
    validate: Callable[[Any], ValidationResult]


@dataclass(frozen=True)
class RunResult:
    """The outcome returned to the Planner's caller."""

    succeeded: bool
    failed_stage: str | None = None
    reason: str | None = None


class Planner:
    """Run and validate stages sequentially while maintaining a daily ledger."""

    def __init__(
        self,
        stages: Iterable[Stage],
        ledger_path: str | Path = "output/ledger.json",
    ) -> None:
        self.stages = list(stages)
        self.ledger_path = Path(ledger_path)

    def run(self) -> RunResult:
        today = date.today().isoformat()
        ledger = self._load_ledger(today)

        for stage in self.stages:
            output: Any = None
            try:
                output = stage.run()
                passed, reason = stage.validate(output)
            except Exception as error:
                reason = f"{type(error).__name__}: {error}"
                self._record(ledger, stage.name, "failed", output, reason)
                return RunResult(False, stage.name, reason)

            status = "done" if passed else "failed"
            self._record(ledger, stage.name, status, output, reason)
            if not passed:
                return RunResult(False, stage.name, reason)

        return RunResult(True)

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
