"""Test StateStore dedup — file JSON lokal, tanpa network."""
import json

from monitor.state import StateStore


def test_set_get_roundtrip(tmp_path):
    store = StateStore(tmp_path / "state.json")
    store.set("target-a", 42)
    assert store.get("target-a") == 42


def test_persist_across_instances(tmp_path):
    path = tmp_path / "state.json"
    StateStore(path).set("harga-buku", 51.77)
    fresh = StateStore(path)
    assert fresh.get("harga-buku") == 51.77


def test_corrupt_file_starts_empty(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{not valid json", encoding="utf-8")
    store = StateStore(path)
    assert store.get("apa-saja") is None


def test_json_on_disk_is_valid(tmp_path):
    path = tmp_path / "state.json"
    store = StateStore(path)
    store.set("t1", "value")
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk == {"t1": "value"}
