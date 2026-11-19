import os

import sys

import unittest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT))

from integrations.telegram_notifier import send_telegram_message

class TestTelegramNotifier(unittest.TestCase):

    def test_missing_configuration_does_not_send(self):

        old_token = os.environ.pop("TELEGRAM_BOT_TOKEN", None)

        old_chat_id = os.environ.pop("TELEGRAM_CHAT_ID", None)

        try:

            result = send_telegram_message("Test CDI")

            self.assertFalse(result)

        finally:

            if old_token is not None:

                os.environ["TELEGRAM_BOT_TOKEN"] = old_token

            if old_chat_id is not None:

                os.environ["TELEGRAM_CHAT_ID"] = old_chat_id

if __name__ == "__main__":

    unittest.main()