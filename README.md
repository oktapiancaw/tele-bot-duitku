
# 💸 DuitKu - Bot Telegram Pencatat Keuangan Anti-Boncos

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg) ![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg) ![uv](https://img.shields.io/badge/uv-Fast_Build-purple.svg)

**DuitKu** adalah bot Telegram pribadi (dan multi-user) yang siap jadi asisten keuangan super bawel. Dibangun dengan arsitektur modern untuk mencatat uang masuk, uang keluar, dan memberikan laporan kejam tentang kondisi dompetmu sebelum akhir bulan tiba. 🚀

## ✨ Fitur Utama
- **Multi-Tenant System:** Bisa dipakai sendiri atau bareng pasangan! Data tiap *user* diisolasi dengan aman di database.
- **Pemasukan & Pengeluaran:** Catat alur uang masuk dan keluar dengan alur percakapan (Conversation Handler) yang interaktif.
- **Kustomisasi Dompet & Kategori:** Bebas bikin kategori (Kopi, Cicilan, Gaji) dan metode bayar (Cash, BCA, e-Wallet) sesukamu.
- **Laporan Instan:** Hasilkan ringkasan finansial Harian, Mingguan, dan Bulanan hanya dengan satu perintah.
- **Super Fast Build:** Di-deploy menggunakan Docker *multi-stage build* dan `uv` dari Astral untuk instalasi *dependency* secepat kilat.

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **Bot Framework:** `python-telegram-bot` (v20+ with Asyncio)
- **Database ORM:** SQLAlchemy 2.0
- **Database Engine:** PostgreSQL (via `psycopg` v3)
- **Deployment:** Docker & Docker Compose
- **Package Manager:** `uv` ⚡

---

## 🚀 Cara Instalasi & Deployment

Karena aplikasi ini sudah dibungkus dengan Docker, nge-jalaninnya gampang banget!

### 1. Persiapan
Pastikan server atau mesin kamu sudah ter-install [Docker](https://docs.docker.com/get-docker/) dan [Docker Compose](https://docs.docker.com/compose/install/).

Dapatkan **Telegram Bot Token** dengan cara chat [@BotFather](https://t.me/BotFather) di Telegram.

### 2. Setup Environment
Ubah token bot kamu di dalam file `docker-compose.yml` pada bagian `environment`:
```yaml
environment:
  - TELEGRAM_BOT_TOKEN=masukkan_token_botfather_di_sini
```

### 3. Build & Run

Buka terminal, masuk ke folder *project*, dan jalankan mantra ini:

```bash
# Menjalankan database dan bot di background
docker compose up -d --build
```

*Note: Docker akan otomatis mengunduh image PostgreSQL dan mem-build image bot menggunakan `uv` dengan sangat efisien.*

### 4. Cek Log (Opsional)

Kalau mau mastiin bot-nya nggak ngambek atau ngecek *error*:

```bash
docker compose logs -f bot
```


## 📖 Buku Panduan (Daftar Perintah)

Buka chat dengan bot kamu di Telegram, lalu ketik perintah ini:

**🚪 Pintu Masuk**

* `/start` - Kenalan sama bot dan mulai pakai.
* `/help` - Nampilin daftar semua perintah.

**⚙️ Konfigurasi Awal (Wajib sebelum nyatet!)**

* `/addcat <masuk/keluar> <nama>` - Bikin kategori. (Contoh: `/addcat keluar Kopi Mumpung Diskon`)
* `/addbill <nama>` - Tambah dompet/rekening. (Contoh: `/addbill Kartu Kredit BCA`)

**💸 Mulai Mencatat**

* `/log` - Mulai alur pencatatan transaksi. Bot bakal nanya tipe, nominal, kategori, dompet, dan catatan.
* `/cancel` - Batalin alur pencatatan kalau tiba-tiba ragu.

**📊 Cek Realita Dompet**

* `/daily` - Laporan hari ini.
* `/weekly` - Laporan 7 hari ke belakang.
* `/monthly` - Laporan 30 hari ke belakang (momen deg-degan).


## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

```text
Copyright (C) 2026 Oktapiancaw
```

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [LICENSE](LICENSE) file for more details.


## Contributors

[//]: contributor-faces

<a href="https://github.com/oktapiancaw"><img src="https://avatars.githubusercontent.com/u/48079010?v=4" title="Oktapian Candra" width="80" height="80" style="border-radius: 50%"></a>

[//]: contributor-faces