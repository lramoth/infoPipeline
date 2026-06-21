"""Runtime loading for pipeline-stage prompt files."""

from __future__ import annotations

from pathlib import Path


class PromptLoadError(RuntimeError):
    """Raised when a required prompt file cannot be loaded or read."""


def load_prompt(path: str | Path) -> str:
    """Return a UTF-8 prompt file's current contents."""
    prompt_path = Path(path)
    try:
        return prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise PromptLoadError(
            f"Required prompt file could not be loaded because it does not exist: {prompt_path}"
        ) from error
    except (OSError, UnicodeError) as error:
        raise PromptLoadError(
            f"Required prompt file could not be read: {prompt_path}: {error}"
        ) from error
