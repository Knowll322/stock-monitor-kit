# Stock Monitor Kit

Monitor harga/stok halaman web 24/7, kirim notifikasi Telegram otomatis saat kondisi terpenuhi.

Dibangun untuk order freelance: pantau stok barang limited, harga kompetitor, ketersediaan tiket — semua dari satu file konfigurasi.

## Fitur

- **Multi-target** — banyak situs dipantau bergiliran, satu config `targets.yaml`
- **Dua mode fetch** — `requests` (halaman statis, cepat) dan `playwright` (halaman JS-rendered)
- **Tiga jenis kondisi** — `in_stock`, `price_below`, `price_change`
- **Notifikasi Telegram** — instan saat kondisi terpenuhi
- **Anti-spam (dedup)** — kondisi yang sama tidak notify dua kali; state disimpan di `state.json`
- **Anti-pola** — interval + jitter ±20% dan rotasi user-agent
- **Tahan gagal** — satu situs error tidak menghentikan monitor situs lain

## Setup

```powershell
# 1. Virtualenv + install
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. (Hanya jika pakai mode playwright) install browser sekali
playwright install chromium

# 3. Konfigurasi
Copy-Item .env.example .env
# Isi TELEGRAM_BOT_TOKEN (dari @BotFather) dan TELEGRAM_CHAT_ID
# Chat id numerik — bisa dapat dari @userinfobot di Telegram

# 4. Tentukan target di targets.yaml (contoh sudah ada)

# 5. Jalankan
python -m monitor
```

## Konfigurasi target (targets.yaml)

```yaml
targets:
  - name: "Sepatu Limited X"          # nama, muncul di notifikasi
    url: "https://toko.example/sepatu"
    fetch_mode: playwright             # requests | playwright
    interval_seconds: 60               # jarak cek
    extract:
      type: text                       # text | attribute | count
      selector: ".price"               # CSS selector
    condition:
      type: price_below                # in_stock | price_below | price_change
      threshold: 499000                # untuk price_below
```

| extract.type | Hasil |
|---|---|
| `count` | jumlah elemen selector (0 = habis) |
| `text` | teks elemen pertama |
| `attribute` | nilai attribute (isi `attribute: href` dsb.) |

## Contoh order klien — langkah custom

1. Klien kirim URL target + apa yang mau dipantau (stok? harga turun?)
2. Buka situs di browser → inspect elemen → salin CSS selector
3. Tentukan `fetch_mode`: coba `requests` dulu, jika data tidak muncul pakai `playwright`
4. Set `condition` sesuai kebutuhan
5. Test lokal 1–2 siklus → deploy

## Deploy

Jalankan terus-menerus di VPS:

```ini
# /etc/systemd/system/stock-monitor.service
[Unit]
Description=Stock Monitor
After=network.target

[Service]
WorkingDirectory=/opt/stock-monitor
ExecStart=/opt/stock-monitor/.venv/bin/python -m monitor
Restart=always
EnvironmentFile=/opt/stock-monitor/.env

[Install]
WantedBy=multi-user.target
```

Alternatif: cron + one-shot mode bisa ditambahkan sesuai kebutuhan order.

## Catatan etis

- Gunakan untuk **monitoring pribadi / riset harga yang wajar**
- Hormati `robots.txt`, ToS situs, dan rate limit — interval terlalu agresif bisa memblokir IP Anda
- Jangan gunakan untuk checkout otomatis, pembelian botongan, atau aktivitas yang melanggar ToS toko — di luar lingkup kit ini

## Test

```powershell
pytest
```

Logika murni (kondisi, parsing harga, dedup state, config) teruji tanpa network.

## Lisensi

MIT
