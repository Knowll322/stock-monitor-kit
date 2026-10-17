"""Strategi pengambilan halaman: requests (statis) dan playwright (JS-rendered)."""
from __future__ import annotations

import logging
import random

import requests
from bs4 import BeautifulSoup

from monitor.config import ExtractSpec, Target

logger = logging.getLogger(__name__)

# User-agent ringan — rotate untuk hindari pola identik
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]


def _extract_from_html(html: str, spec: ExtractSpec):
    """Ekstrak nilai dari HTML sesuai ExtractSpec."""
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.select(spec.selector)

    if spec.type == "count":
        return len(elements)
    if not elements:
        return None
    el = elements[0]
    if spec.type == "attribute":
        return el.get(spec.attribute)
    return el.get_text(strip=True)


def fetch_with_requests(url: str, spec: ExtractSpec, timeout: float = 20.0):
    headers = {"User-Agent": random.choice(_USER_AGENTS)}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return _extract_from_html(resp.text, spec)


def fetch_with_playwright(url: str, spec: ExtractSpec, timeout_ms: int = 30_000):
    """Butuh `playwright install chromium` sekali di awal."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(user_agent=random.choice(_USER_AGENTS))
            page.goto(url, timeout=timeout_ms, wait_until="networkidle")
            html = page.content()
        finally:
            browser.close()
    return _extract_from_html(html, spec)


def fetch_value(target: Target):
    """Fetch sesuai fetch_mode target. Raise exception jika gagal (ditangkap pemanggil)."""
    if target.fetch_mode == "playwright":
        return fetch_with_playwright(target.url, target.extract)
    if target.fetch_mode == "requests":
        return fetch_with_requests(target.url, target.extract)
    raise ValueError(f"fetch_mode tidak dikenal: {target.fetch_mode} (target: {target.name})")
