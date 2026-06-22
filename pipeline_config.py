"""Load and assemble pipeline stages from the project YAML configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from curator import Curator
from researcher import Researcher
from writer import Writer


PROJECT_ROOT = Path(__file__).parent
CONFIG_PATH = PROJECT_ROOT / "config" / "pipeline.yaml"

STAGE_TYPES = {
    "researcher": Researcher,
    "curator": Curator,
    "writer": Writer,
}


class PipelineConfigError(RuntimeError):
    """Raised when the pipeline configuration cannot be loaded or assembled."""


def load_pipeline_config() -> list[Researcher | Curator | Writer]:
    """Return configured stage instances in YAML order without running them."""
    config = _read_config()
    stage_entries = config.get("stages") if isinstance(config, dict) else None
    if not isinstance(stage_entries, list):
        raise PipelineConfigError("Pipeline configuration must contain a stages list")

    return [_assemble_stage(entry, index) for index, entry in enumerate(stage_entries)]


def load_pipeline() -> list[Researcher | Curator | Writer]:
    """Return the stages assembled from the project's pipeline configuration."""
    return load_pipeline_config()


def _read_config() -> Any:
    try:
        with CONFIG_PATH.open(encoding="utf-8") as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError as error:
        raise PipelineConfigError(
            f"Pipeline configuration file does not exist: {CONFIG_PATH}"
        ) from error
    except yaml.YAMLError as error:
        raise PipelineConfigError(f"Pipeline configuration YAML is malformed: {error}") from error
    except OSError as error:
        raise PipelineConfigError(
            f"Pipeline configuration file could not be read: {CONFIG_PATH}: {error}"
        ) from error


def _assemble_stage(entry: Any, index: int) -> Researcher | Curator | Writer:
    if not isinstance(entry, dict):
        raise PipelineConfigError(f"Stage entry {index} must be an object")

    name = entry.get("name")
    if not isinstance(name, str) or not name:
        raise PipelineConfigError(f"Stage entry {index} is missing required field: name")
    if name not in STAGE_TYPES:
        raise PipelineConfigError(f"Unknown stage name: {name}")

    prompt_path = entry.get("prompt_path")
    if not isinstance(prompt_path, str) or not prompt_path:
        raise PipelineConfigError(f"Stage {name} is missing required field: prompt_path")

    resolved_prompt_path = PROJECT_ROOT / prompt_path
    if not resolved_prompt_path.is_file():
        raise PipelineConfigError(
            f"Configured prompt file does not exist for stage {name}: {resolved_prompt_path}"
        )

    constructor_args: dict[str, Any] = {"prompt_path": resolved_prompt_path}
    model = entry.get("model")
    if model is not None:
        if not isinstance(model, dict):
            raise PipelineConfigError(f"Model for stage {name} must be an object")
        for required_field in ("provider", "name"):
            if not isinstance(model.get(required_field), str) or not model[required_field]:
                raise PipelineConfigError(
                    f"Model for stage {name} is missing required field: {required_field}"
                )
        constructor_args["model"] = model["name"]
        if "endpoint" in model:
            if not isinstance(model["endpoint"], str) or not model["endpoint"]:
                raise PipelineConfigError(
                    f"Model endpoint for stage {name} must be a non-empty string"
                )
            constructor_args["endpoint"] = model["endpoint"]

    return STAGE_TYPES[name](**constructor_args)
