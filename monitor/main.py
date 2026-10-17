"""Loop monitoring utama: cek tiap target secara bergiliran, notifikasi saat kondisi terpenuhi."""
from __future__ import annotations

import logging
import random
import time

from monitor.conditions import evaluate, parse_price
from monitor.config import Settings, Target
from monitor.fetcher import fetch_value
from monitor.notifier import send_telegram
from monitor.state import StateStore

logger = logging.getLogger(__name__)


def check_target(target: Target, state: StateStore, settings: Settings) -> bool:
    """Cek satu target. Return True jika notifikasi terkirim."""
    try:
        value = fetch_value(target)
    except Exception:
        # Satu target gagal tidak boleh menghentikan target lain
        logger.exception("Gagal fetch target %s (%s)", target.name, target.url)
        return False

    previous = state.get(target.name)
    triggered = evaluate(target.condition.type, value, target.condition.threshold, previous)

    if triggered:
        # Untuk price_change, update state hanya jika terpicu supaya perubahan berikutnya tetap terdeteksi.
        # Untuk tipe lain, update state selalu (dedup: tidak notify dua kali selama kondisi sama).
        if target.condition.type == "price_change" or previous is None or previous != value:
            msg = _format_message(target, value, previous)
            sent = send_telegram(settings.telegram_token, settings.telegram_chat_id, msg)
            if sent:
                state.set(target.name, value)
                return True
    else:
        # Kondisi tidak terpenuhi — update state agar price_change tahu baseline
        if previous != value:
            state.set(target.name, value)

    return False


def _format_message(target: Target, value, previous) -> str:
    ctype = target.condition.type
    if ctype == "in_stock":
        body = f"✅ Stok terdeteksi: <b>{value}</b>"
    elif ctype == "price_below":
        body = f"💰 Harga di bawah threshold: <b>{value}</b> (limit {target.condition.threshold})"
    elif ctype == "price_change":
        body = f"🔄 Harga berubah: {previous} → <b>{value}</b>"
    else:
        body = f"🔔 Kondisi terpenuhi: <b>{value}</b>"
    return f"<b>{target.name}</b>\n{body}\n{target.url}"


def run_forever(settings: Settings, state_path: str = "state.json") -> None:
    """Loop utama. Setiap target dicek pada intervalnya + jitter ±20% anti-pola."""
    if not settings.targets:
        logger.error("Tidak ada target di targets.yaml — berhenti.")
        return

    state = StateStore(state_path)
    next_check: dict[str, float] = {t.name: 0.0 for t in settings.targets}

    logger.info("Monitor mulai: %d target aktif", len(settings.targets))
    while True:
        now = time.monotonic()
        for target in settings.targets:
            if now < next_check[target.name]:
                continue
            check_target(target, state, settings)
            jitter = target.interval_seconds * random.uniform(-0.2, 0.2)
            next_check[target.name] = time.monotonic() + max(5.0, target.interval_seconds + jitter)
        time.sleep(1.0)
