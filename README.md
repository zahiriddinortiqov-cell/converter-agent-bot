# 📄 Converter Agent Bot

Telegram bot: **PDF ↔ Word**, rasm konvertatsiyasi va **OCR** (uzb/rus/eng). 3 tilda javob beradi.

![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Imkoniyatlar

| Yuborasiz | Natija | Usul |
|---|---|---|
| PDF (matnli) | DOCX | pdf2docx |
| PDF (skanerlangan) | DOCX | OCR (tesseract) |
| DOCX | PDF | LibreOffice |
| TXT | PDF | LibreOffice |
| JPG/PNG/WEBP/BMP/TIFF | PDF | Pillow |
| Rasm | DOCX | OCR |
| Rasm | PNG | Pillow |

- 🌍 3 til: o'zbek, rus, ingliz (`/lang` bilan almashtiriladi)
- 🧠 Smart-routing: matnli/skannerlangan PDF ni avtomatik farqlaydi
- 🐳 Docker + webhook (Caddy/nginx reverse proxy bilan)

## 🚀 Tez boshlash

### 1. GitHub'dan yuklab olish
```bash
git clone https://github.com/SIZNING-USERNAME/converter-agent-bot.git
cd converter-agent-bot
```

### 2. Token olish
1. Telegram'da [@BotFather](https://t.me/BotFather) ga kiring
2. `/newbot` → nom bering → **token** olasiz (masalan `123456:ABC...`)

### 3. Ishga tushirish — 2 yo'l

**A. Polling (oddiy, domen shart emas):**
```bash
pip install -r requirements.txt
sudo apt install libreoffice-writer tesseract-ocr tesseract-ocr-uzb tesseract-ocr-rus tesseract-ocr-eng
BOT_TOKEN=123456:ABC... MODE=polling python bot.py
```

**B. Docker + webhook:**
```bash
cp .env.example .env   # token va domenni yozing
docker compose up -d --build
```

Caddy reverse proxy (avtomatik HTTPS):
```
meningbot.uz
reverse_proxy localhost:8080
```

## ⚙️ Muhit o'zgaruvchilari (.env)

| O'zgaruvchi | Tavsif |
|---|---|
| `BOT_TOKEN` | @BotFather token (majburiy) |
| `MODE` | `polling` yoki `webhook` |
| `WEBHOOK_URL` | `https://meningbot.uz` — webhook uchun |
| `PORT` | Standart: 8080 |

## 🏗 Arxitektura

```
bot.py        — Telegram webhook/polling, i18n, handlerlar
converters.py — PDF/Word/rasm konvertatsiya logikasi
i18n.py       — UZ/RU/EN matnlar
Dockerfile    — LibreOffice + Tesseract + Python barcha bitta
```

## ⚠️ Cheklovlar

- OCR sifati rasm sifatiga bog'liq (300 DPI skan — ideal)
- Murakkab jadvallar OCR da matn ko'rinishida chiqadi
- Himoyalangan (parollı) PDF lar ochilmaydi

## 📄 Litsenziya

MIT — erkin ishlating, o'zgartiring, tarqating.
