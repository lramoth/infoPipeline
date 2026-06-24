import tempfile
import unittest
from pathlib import Path

from env_config import EnvConfigError, load_env_value


class EnvConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.env_path = Path(self.temporary_directory.name) / ".env"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_loads_all_external_service_values(self):
        self.env_path.write_text(
            "GEMINI_API_KEY=gemini-secret\n"
            "TELEGRAM_BOT_TOKEN='telegram-secret'\n"
            'TELEGRAM_CHAT_ID="12345"\n',
            encoding="utf-8",
        )

        self.assertEqual(load_env_value("GEMINI_API_KEY", self.env_path), "gemini-secret")
        self.assertEqual(
            load_env_value("TELEGRAM_BOT_TOKEN", self.env_path), "telegram-secret"
        )
        self.assertEqual(load_env_value("TELEGRAM_CHAT_ID", self.env_path), "12345")

    def test_raises_when_env_file_does_not_exist(self):
        with self.assertRaisesRegex(EnvConfigError, "does not exist"):
            load_env_value("GEMINI_API_KEY", self.env_path)

    def test_raises_when_required_key_is_missing(self):
        self.env_path.write_text("GEMINI_API_KEY=secret\n", encoding="utf-8")

        with self.assertRaisesRegex(EnvConfigError, "TELEGRAM_BOT_TOKEN"):
            load_env_value("TELEGRAM_BOT_TOKEN", self.env_path)


if __name__ == "__main__":
    unittest.main()
