import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from delivery import TelegramDelivery, TelegramDeliveryError


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class TelegramDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.env_path = Path(self.temporary_directory.name) / ".env"
        self.env_path.write_text(
            "TELEGRAM_BOT_TOKEN=bot-token\nTELEGRAM_CHAT_ID=chat-123\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_sends_outbound_message_unchanged_to_configured_telegram_chat(self):
        seen_payload = None

        def fake_urlopen(request):
            nonlocal seen_payload
            seen_payload = json.loads(request.data.decode("utf-8"))
            self.assertEqual(
                request.full_url,
                "https://telegram.example/botbot-token/sendMessage",
            )
            self.assertEqual(request.get_method(), "POST")
            return FakeResponse(b'{"ok": true}')

        with patch("delivery.urllib.request.urlopen", side_effect=fake_urlopen):
            result = TelegramDelivery(
                endpoint="https://telegram.example",
                env_path=self.env_path,
            ).deliver("final outbound message")

        self.assertTrue(result.succeeded)
        self.assertEqual(result.provider, "telegram")
        self.assertEqual(
            seen_payload,
            {"chat_id": "chat-123", "text": "final outbound message"},
        )

    def test_reports_telegram_transport_failure(self):
        with patch(
            "delivery.urllib.request.urlopen",
            side_effect=urllib.error.URLError("unreachable"),
        ):
            with self.assertRaisesRegex(TelegramDeliveryError, "Telegram delivery failed"):
                TelegramDelivery(
                    endpoint="https://telegram.example",
                    env_path=self.env_path,
                ).deliver("final outbound message")

    def test_reports_telegram_rejection_as_delivery_failure(self):
        with patch(
            "delivery.urllib.request.urlopen",
            return_value=FakeResponse(b'{"ok": false, "description": "chat not found"}'),
        ):
            with self.assertRaisesRegex(TelegramDeliveryError, "chat not found"):
                TelegramDelivery(
                    endpoint="https://telegram.example",
                    env_path=self.env_path,
                ).deliver("final outbound message")


if __name__ == "__main__":
    unittest.main()
