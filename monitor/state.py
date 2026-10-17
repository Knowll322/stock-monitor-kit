"""State dedup: simpan nilai terakhir per target di file JSON lokal.

Tujuan: notifikasi yang sama tidak dikirim berulang selama kondisi masih
terpenuhi (mis. stok masih ada, harga masih di bawah threshold).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class StateStore:
    def __init__(self, path: str | Path = "state.json"):
        self._path = Path(path)
        self._state: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._state = json.loads(self._path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                logger.warning("State file rusak/tidak terbaca, mulai dari kosong: %s", self._path)
                self._state = {}

    def get(self, target_name: str) -> Any:
        return self._state.get(target_name)

    def set(self, target_name: str, value: Any) -> None:
        self._state[target_name] = value
        self._save()

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self._state, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self._path)  # atomic-ish, hindari file setengah tertulis
        except OSError:
            logger.exception("Gagal menyimpan state ke %s", self._path)
