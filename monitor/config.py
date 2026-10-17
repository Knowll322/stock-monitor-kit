"""Muat konfigurasi target dari targets.yaml + .env."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class ExtractSpec:
    type: str  # text | attribute | count
    selector: str
    attribute: str = ""


@dataclass(frozen=True)
class Condition:
    type: str  # in_stock | price_below | price_change
    threshold: float = 0.0


@dataclass(frozen=True)
class Target:
    name: str
    url: str
    fetch_mode: str
    interval_seconds: int
    extract: ExtractSpec
    condition: Condition


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    telegram_chat_id: str
    targets: tuple[Target, ...]


def _parse_target(raw: dict[str, Any], default_mode: str) -> Target:
    extract_raw = raw.get("extract", {}) or {}
    condition_raw = raw.get("condition", {}) or {}
    return Target(
        name=str(raw.get("name", "Tanpa Nama")),
        url=str(raw.get("url", "")),
        fetch_mode=str(raw.get("fetch_mode", default_mode)),
        interval_seconds=int(raw.get("interval_seconds", 300)),
        extract=ExtractSpec(
            type=str(extract_raw.get("type", "text")),
            selector=str(extract_raw.get("selector", "")),
            attribute=str(extract_raw.get("attribute", "")),
        ),
        condition=Condition(
            type=str(condition_raw.get("type", "in_stock")),
            threshold=float(condition_raw.get("threshold", 0.0)),
        ),
    )


def load_settings(config_path: str | Path = "targets.yaml") -> Settings:
    load_dotenv()

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} tidak ditemukan. Salin targets.yaml.example atau buat targets.yaml."
        )

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    default_mode = os.getenv("DEFAULT_FETCH_MODE", "requests").strip() or "requests"
    raw_targets = data.get("targets", []) or []
    targets = tuple(_parse_target(t, default_mode) for t in raw_targets if t.get("url"))

    names = [t.name for t in targets]
    if len(names) != len(set(names)):
        raise ValueError("Nama target di targets.yaml harus unik.")

    return Settings(
        telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        targets=targets,
    )
