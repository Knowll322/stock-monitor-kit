"""Logika kondisi notifikasi — murni, tanpa network, mudah dites."""
from __future__ import annotations

import re
from typing import Any


def parse_price(raw: str) -> float | None:
    """Ekstrak angka harga dari teks seperti '£51.77' atau 'Rp 1.250.000'.

    Koma/ titik pemisah ribuan lokal dipahami secara longgar:
    - '£51.77'  -> 51.77
    - 'Rp1.250.000' -> 1250000 (jika dua blok 3-digit setelah pemisah -> ribuan)
    """
    if raw is None:
        return None
    cleaned = re.sub(r"[^\d.,]", "", str(raw).strip())
    if not cleaned:
        return None

    if "," in cleaned and "." in cleaned:
        # Pemisah terakhir adalah desimal
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        parts = cleaned.split(",")
        # '1,25' -> desimal; '1.250.000' style pakai titik, jadi koma di sini kemungkinan desimal
        cleaned = cleaned.replace(",", ".") if len(parts[-1]) != 3 else cleaned.replace(",", "")
    elif "." in cleaned:
        parts = cleaned.split(".")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3):
            cleaned = cleaned.replace(".", "")

    try:
        return float(cleaned)
    except ValueError:
        return None


def evaluate(condition_type: str, value: Any, threshold: float = 0.0, previous: Any = None) -> bool:
    """Return True jika notifikasi harus dikirim.

    condition_type:
      - in_stock     : value (count/teks) dianggap "ada" jika > 0 / non-kosong
      - price_below  : harga value < threshold
      - price_change : harga value berbeda dari previous
    """
    if condition_type == "in_stock":
        if isinstance(value, (int, float)):
            return value > 0
        return bool(str(value).strip())

    if condition_type == "price_below":
        price = value if isinstance(value, (int, float)) else parse_price(str(value))
        if price is None:
            return False
        return price < threshold

    if condition_type == "price_change":
        price = value if isinstance(value, (int, float)) else parse_price(str(value))
        prev = previous if isinstance(previous, (int, float)) else parse_price(str(previous or ""))
        if price is None or prev is None:
            return False
        return abs(price - prev) > 1e-9

    return False
