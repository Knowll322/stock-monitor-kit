"""Test logika harga & kondisi — murni, tanpa network."""
from monitor.conditions import evaluate, parse_price


# --- parse_price ---

def test_parse_price_english_decimal():
    assert parse_price("£51.77") == 51.77


def test_parse_price_plain_number():
    assert parse_price("150000") == 150000.0


def test_parse_price_rp_thousands():
    assert parse_price("Rp 1.250.000") == 1250000.0


def test_parse_price_comma_decimal():
    assert parse_price("12,50") == 12.5


def test_parse_price_garbage():
    assert parse_price("hubungi kami") is None
    assert parse_price("") is None


# --- evaluate in_stock ---

def test_in_stock_count_positive():
    assert evaluate("in_stock", 5) is True


def test_in_stock_count_zero():
    assert evaluate("in_stock", 0) is False


def test_in_stock_text_nonempty():
    assert evaluate("in_stock", "Tersedia") is True


def test_in_stock_text_empty():
    assert evaluate("in_stock", "   ") is False


# --- evaluate price_below ---

def test_price_below_true():
    assert evaluate("price_below", "£15.00", threshold=20.0) is True


def test_price_below_false():
    assert evaluate("price_below", "£25.00", threshold=20.0) is False


def test_price_below_unparseable():
    assert evaluate("price_below", "harga", threshold=20.0) is False


# --- evaluate price_change ---

def test_price_change_detected():
    assert evaluate("price_change", "£10.00", previous="£12.00") is True


def test_price_change_same():
    assert evaluate("price_change", "£10.00", previous="£10.00") is False


def test_price_change_no_previous():
    assert evaluate("price_change", "£10.00", previous=None) is False
