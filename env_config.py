"""Load external-service configuration from the project's .env file."""

from __future__ import annotations

from pathlib import Path


PROJECT_ENV_PATH = Path(__file__).resolve().parent / ".env"


class EnvConfigError(RuntimeError):
    """Raised when required project configuration cannot be loaded."""


def load_env_value(key: str, env_path: str | Path = PROJECT_ENV_PATH) -> str:
    """Return a required value from an .env file."""
    path = Path(env_path)
    if not path.is_file():
        raise EnvConfigError(f"Environment file does not exist: {path}")

    values: dict[str, str] = {}
    with path.open(encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[name] = value

    if not values.get(key):
        raise EnvConfigError(f"Required key is missing from {path}: {key}")
    return values[key]
