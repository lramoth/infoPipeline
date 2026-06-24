"""Pure-Python coordinator for the infoPipeline stages."""

from __future__ import annotations

import json
import inspect
import sys
import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from delivery import DeliveryResult
from diagnostics import write_diagnostic
from pipeline_config import load_delivery_config, load_pipeline, profile_ledger_path, resolve_profile_name


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
    failed_delivery: str | None = None
    delivery_results: list[DeliveryResult] | None = None


class Planner:
    """Run and validate stages sequentially while maintaining a daily ledger."""

    def __init__(
        self,
        stages: Iterable[Any] | None = None,
        ledger_path: str | Path | None = None,
        delivery_providers: Iterable[Any] | None = None,
        profile_name: str | None = None,
    ) -> None:
        using_default_pipeline = stages is None
        self.profile_name = (
            resolve_profile_name(profile_name)
            if using_default_pipeline
            else profile_name
        )
        self.stages = list(
            load_pipeline(self.profile_name) if using_default_pipeline else stages
        )
        if delivery_providers is None:
            self.delivery_providers = list(
                load_delivery_config() if using_default_pipeline else []
            )
        else:
            self.delivery_providers = list(delivery_providers)
        if ledger_path is None:
            if using_default_pipeline:
                ledger_path = profile_ledger_path(self.profile_name)
            else:
                ledger_path = "output/ledger.json"
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

        delivery_results = self._deliver(ledger, previous_output)
        failed_delivery = next(
            (result for result in delivery_results if not result.succeeded),
            None,
        )
        if failed_delivery is not None:
            return RunResult(
                False,
                previous_output,
                failed_delivery=failed_delivery.provider,
                reason=failed_delivery.reason,
                delivery_results=delivery_results,
            )

        return RunResult(True, previous_output, delivery_results=delivery_results)

    def _load_ledger(self, today: str) -> dict[str, Any]:
        ledger = {"date": today, "stages": {}}
        if self.profile_name is not None:
            ledger["profile"] = self.profile_name
        return ledger

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

    def _deliver(
        self,
        ledger: dict[str, Any],
        message: Any,
    ) -> list[DeliveryResult]:
        results = []
        for provider in self.delivery_providers:
            provider_name = self._delivery_provider_name(provider)
            try:
                result = provider.deliver(message)
                if not isinstance(result, DeliveryResult):
                    result = DeliveryResult(provider_name, True, "Delivery succeeded")
            except Exception as error:
                reason = f"{type(error).__name__}: {error}"
                result = DeliveryResult(provider_name, False, reason)
            self._record_delivery(ledger, result)
            results.append(result)
        return results

    def _record_delivery(
        self,
        ledger: dict[str, Any],
        result: DeliveryResult,
    ) -> None:
        entry = {
            "provider": result.provider,
            "status": "done" if result.succeeded else "failed",
            "reason": result.reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        ledger.setdefault("delivery", {})[result.provider] = entry
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

    def _delivery_provider_name(self, provider: Any) -> str:
        return getattr(provider, "name", provider.__class__.__name__.lower())

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


def main(argv: list[str] | None = None) -> int:
    """Run the default configured pipeline once from the command line."""
    parser = argparse.ArgumentParser(description="Run the configured infoPipeline once.")
    parser.add_argument(
        "--profile",
        dest="profile_name",
        help="Configured profile to run. Defaults to config/pipeline.yaml default_profile.",
    )
    args = parser.parse_args(argv)

    try:
        result = Planner(profile_name=args.profile_name).run()
    except Exception as error:
        print(f"Pipeline failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 1

    if result.succeeded:
        print(_format_cli_output(result.output))
        return 0

    if result.failed_delivery:
        print(_format_cli_output(result.output))
        print(
            f"Delivery failed for {result.failed_delivery}: {result.reason}",
            file=sys.stderr,
        )
        return 1

    failed_stage = result.failed_stage or "unknown stage"
    reason = result.reason or "no failure reason provided"
    print(f"Pipeline failed at {failed_stage}: {reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
