"""Jalankan dengan: python -m monitor"""
import logging

from monitor.config import load_settings
from monitor.main import run_forever

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def main() -> None:
    settings = load_settings()
    if not settings.telegram_token or not settings.telegram_chat_id:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID belum diisi. Salin .env.example menjadi .env lalu isi."
        )
    run_forever(settings)


if __name__ == "__main__":
    main()
