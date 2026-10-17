# Bot Zen — demo offline stock monitor: fetch nyata dari books.toscrape.com
# (situs demo publik), notifikasi dicetak ke layar (tanpa Telegram).

    python demo.py

Rekam layar terminal untuk video portofolio.
"""
from __future__ import annotations

import time

from monitor.conditions import evaluate, parse_price
from monitor.config import Condition, ExtractSpec, Target
from monitor.fetcher import fetch_value
from monitor.state import StateStore

DEMO_TARGETS = [
    Target(
        name="Demo Jumlah Buku",
        url="https://books.toscrape.com/catalogue/page-1.html",
        fetch_mode="requests",
        interval_seconds=5,
        extract=ExtractSpec(type="count", selector="article.product_pod"),
        condition=Condition(type="in_stock"),
    ),
    Target(
        name="Demo Harga Buku Termurah",
        url="https://books.toscrape.com/catalogue/page-1.html",
        fetch_mode="requests",
        interval_seconds=5,
        extract=ExtractSpec(type="text", selector=".product_price .price_color"),
        condition=Condition(type="price_below", threshold=999.0),
    ),
]


def _banner(text: str) -> None:
    print("\n" + "=" * 56)
    print(f"  {text}")
    print("=" * 56)


def demo_cycle(state: StateStore, cycle: int) -> None:
    _banner(f"SIKLUS {cycle}")
    for target in DEMO_TARGETS:
        print(f"\n[{target.name}]")
        print(f"  URL   : {target.url}")
        print(f"  Ambil : {target.extract.type} via selector '{target.extract.selector}'")
        time.sleep(0.4)

        try:
            value = fetch_value(target)
        except Exception as exc:
            print(f"  Gagal : {exc}")
            continue

        print(f"  Nilai : {value}")

        prev = state.get(target.name)
        triggered = evaluate(target.condition.type, value, target.condition.threshold, prev)
        if triggered:
            if target.condition.type == "in_stock":
                msg = f"Stok terdeteksi: {value} item"
            else:
                price = parse_price(str(value))
                msg = f"Harga di bawah threshold: {price} (limit {target.condition.threshold})"
            print(f"  >>> NOTIFIKASI TELEGRAM <<<")
            print(f"      {target.name}")
            print(f"      {msg}")
            print(f"      {target.url}")
            state.set(target.name, value)
        else:
            print(f"  Kondisi tidak terpenuhi — state diperbarui, tanpa notifikasi (anti-spam)")
            if prev != value:
                state.set(target.name, value)
        time.sleep(0.4)


def main() -> None:
    print("BOT ZEN — Stock Monitor Kit Demo")
    print("Fetch nyata ke books.toscrape.com, notifikasi simulasi di layar. | t.me/botzen")
    state = StateStore("state_demo.json")
    for cycle in (1, 2):
        demo_cycle(state, cycle)
        if cycle == 1:
            print("\n  (Siklus 2 memakai state yang sama — notifikasi tidak dobel)")
            time.sleep(0.6)
    _banner("SELESAI — 2 siklus penuh")
    print("Untuk live: isi TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID di .env, jalankan python -m monitor\n")


if __name__ == "__main__":
    main()
