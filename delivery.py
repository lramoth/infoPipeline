"""Delivery providers for completed outbound messages."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from diagnostics import DiagnosticError, external_http_context
from env_config import PROJECT_ENV_PATH, load_env_value


TELEGRAM_ENDPOINT = "https://api.telegram.org"


@dataclass(frozen=True)
class DeliveryResult:
    """Observable outcome from a delivery provider."""

    provider: str
    succeeded: bool
    reason: str


class TelegramDeliveryError(DiagnosticError):
    """Raised when Telegram delivery cannot transport the outbound message."""


class TelegramDelivery:
    """Transport outbound messages to the configured Telegram chat."""

    name = "telegram"

    def __init__(
        self,
        endpoint: str = TELEGRAM_ENDPOINT,
        env_path: str | Path = PROJECT_ENV_PATH,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.env_path = Path(env_path)

    def deliver(self, message: str) -> DeliveryResult:
        """Send the outbound message without changing it."""
        bot_token = load_env_value("TELEGRAM_BOT_TOKEN", self.env_path)
        chat_id = load_env_value("TELEGRAM_CHAT_ID", self.env_path)
        url = f"{self.endpoint}/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request) as response:
                api_response = json.load(response)
        except urllib.error.URLError as error:
            raise TelegramDeliveryError(
                f"Telegram delivery failed: {error}",
                external_http_context("Telegram", "sendMessage", request, error),
            ) from error
        except json.JSONDecodeError as error:
            raise TelegramDeliveryError(
                f"Telegram delivery failed: {error}",
                {
                    "failure_category": "external_http_call",
                    "provider_name": "Telegram",
                    "model_name": "sendMessage",
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "parse_error_message": str(error),
                },
            ) from error

        if api_response.get("ok") is not True:
            description = api_response.get("description") or "Telegram rejected delivery"
            raise TelegramDeliveryError(
                f"Telegram delivery failed: {description}",
                {
                    "failure_category": "external_http_call",
                    "provider_name": "Telegram",
                    "model_name": "sendMessage",
                    "endpoint_url": request.full_url,
                    "http_method": request.get_method(),
                    "response_body": api_response,
                },
            )

        return DeliveryResult("telegram", True, "Delivery succeeded")
