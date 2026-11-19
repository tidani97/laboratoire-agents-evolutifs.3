

import os

import json

import urllib.request

import urllib.error

def send_telegram_message(message: str) -> bool:

    """Send a notification to the authorized CDI Telegram chat."""

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:

        print("Telegram non configure : notification ignoree.")

        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {

        "chat_id": chat_id,

        "text": f"CDI-TRADER\n\n{message}"

    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(

        url,

        data=data,

        headers={"Content-Type": "application/json"},

        method="POST"

    )

    try:

        with urllib.request.urlopen(request, timeout=10) as response:

            result = json.loads(response.read().decode("utf-8"))

            return result.get("ok", False)

    except (urllib.error.URLError, TimeoutError, ValueError) as error:

        print(f"Erreur Telegram : {error}")

        return False