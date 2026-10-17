"""Kirim notifikasi Telegram. Sederhana: satu chat id tujuan."""
from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


def send_telegram(token: str, chat_id: str, text: str, timeout: float = 15.0) -> bool:
    if not token or not chat_id:
        logger.warning("Telegram token/chat id kosong, notifikasi dilewati.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=timeout,
        )
        resp.raise_for_status()
        return True
    except requests.RequestException:
        logger.exception("Gagal kirim notifikasi Telegram")
        return False
