"""Test parser targets.yaml — tanpa network."""
import pytest

from monitor.config import load_settings


VALID_YAML = """
targets:
  - name: "Demo Satu"
    url: "https://books.toscrape.com/"
    interval_seconds: 60
    extract:
      type: count
      selector: "article.product_pod"
    condition:
      type: in_stock
  - name: "Demo Dua"
    url: "https://example.com"
    fetch_mode: playwright
    extract:
      type: text
      selector: ".price"
    condition:
      type: price_below
      threshold: 25.5
"""


def test_load_valid_config(tmp_path, monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("DEFAULT_FETCH_MODE", raising=False)
    cfg = tmp_path / "targets.yaml"
    cfg.write_text(VALID_YAML, encoding="utf-8")

    settings = load_settings(cfg)
    assert len(settings.targets) == 2

    t1, t2 = settings.targets
    assert t1.name == "Demo Satu"
    assert t1.fetch_mode == "requests"  # default ketika tidak diset
    assert t1.condition.type == "in_stock"

    assert t2.fetch_mode == "playwright"
    assert t2.condition.threshold == 25.5


def test_duplicate_names_rejected(tmp_path):
    cfg = tmp_path / "targets.yaml"
    cfg.write_text(
        """
targets:
  - name: "Sama"
    url: "https://a.example"
    extract: {type: count, selector: "div"}
    condition: {type: in_stock}
  - name: "Sama"
    url: "https://b.example"
    extract: {type: count, selector: "div"}
    condition: {type: in_stock}
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unik"):
        load_settings(cfg)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_settings(tmp_path / "hilang.yaml")
