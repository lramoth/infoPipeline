"""Provider-configured collector for the Researcher pipeline stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from env_config import PROJECT_ENV_PATH
from prompt_loader import PromptLoadError, load_prompt
from researcher_providers.errors import ResearcherError
from researcher_providers.gemini import GeminiResearcherProvider
from researcher_providers.openai import OpenAIResearcherProvider


GEMINI_MODEL = "gemini-2.5-flash"
PROVIDER_GEMINI = "gemini"
PROVIDER_OPENAI = "openai"


class Researcher:
    """Collect and validate configured-topic research from the selected provider."""

    def __init__(
        self,
        prompt_path: str | Path,
        endpoint: str,
        provider: str = PROVIDER_GEMINI,
        model: str = GEMINI_MODEL,
        env_path: str | Path = PROJECT_ENV_PATH,
    ) -> None:
        self.provider = provider
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.env_path = Path(env_path)
        self.prompt_path = Path(prompt_path)

    def run(self) -> dict[str, Any]:
        """Search with the configured provider and return normalized research output."""
        try:
            prompt = load_prompt(self.prompt_path)
        except PromptLoadError as error:
            raise ResearcherError(str(error)) from error

        if self.provider == PROVIDER_GEMINI:
            return GeminiResearcherProvider(
                self.model,
                self.endpoint,
                self.env_path,
            ).run(prompt)
        if self.provider == PROVIDER_OPENAI:
            return OpenAIResearcherProvider(
                self.model,
                self.endpoint,
                self.env_path,
            ).run(prompt)

        raise ResearcherError(f"Unsupported Researcher model provider: {self.provider}")

    @staticmethod
    def validate(output: Any) -> tuple[bool, str]:
        """Validate the provider-neutral item count and required item fields."""
        if not isinstance(output, dict) or not isinstance(output.get("items"), list):
            return False, "Researcher output does not contain an items list"

        items = output["items"]
        if len(items) < 3:
            return False, "Researcher output contains fewer than 3 items"

        required_fields = ("title", "url", "summary")
        for index, item in enumerate(items):
            if not isinstance(item, dict) or any(not item.get(field) for field in required_fields):
                return False, f"Research item {index} is missing a title, url, or summary"

        return True, "At least 3 items contain a title, url, and summary"
