# 📄 Converter Agent Bot

Telegram bot: **PDF / Word / Excel / Rasm / Matn** konvertatsiyasi + **OCR** (uzb/rus/eng), 3 tilda, tugmalar bilan.

![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Imkoniyatlar

Fayl yuboring — bot **qaysi format kerakligini tugmalar bilan so'raydi**:

| Yuborasiz | Tugmalar |
|---|---|
| PDF | 📝 Word · 📊 Excel · 🖼️ PNG · 📃 TXT |
| Word (DOCX) | 📄 PDF · 📃 TXT · 🖼️ PNG |
| Excel (XLSX) | 📄 PDF · 🖼️ PNG |
| Matn (TXT) | 📄 PDF · 📝 Word |
| Rasm (JPG/PNG/WEBP/BMP/TIFF) | 📄 PDF · 🖼️ PNG · 📝 Word (OCR) |

- 🌍 3 til: startda til tanlanadi, `/lang` bilan almashtiriladi
- 🧠 Smart: skanerlangan PDF avtomatik OCR ga tushadi
- 📦 Ko'p sahifali PDF -> rasmlar ZIP arxivda qaytadi

## 🚀 Ishga tushirish

### Render.com (eng oson)
1. GitHub'ga repo'ni joylang
2. Render'da **New Web Service** → repo'ni tanlang
3. Environment Variables:
   - `BOT_TOKEN` — @BotFather token
   - `MODE` = `webhook`
   - `WEBHOOK_URL` = `https://SIZNING-XIZMAT.onrender.com`
4. **Deploy** tugmasi

### Lokal (polling)
```bash
pip install -r requirements.txt
sudo apt install libreoffice-writer libreoffice-calc tesseract-ocr tesseract-ocr-uzb tesseract-ocr-rus tesseract-ocr-eng
BOT_TOKEN=... MODE=polling python bot.py
```

### Docker + webhook
```bash
cp .env.example .env
docker compose up -d --build
```

## ⚠️ Cheklovlar

- **PDF -> Excel**: oddiy jadvallar yaxshi chiqadi; murakkab maketlarda qatorlar buzilishishi mumkin (jadval topilmasa matn bir ustunga yoziladi)
- OCR sifati rasm saratiga bog'liq (300 DPI skan — ideal)
- Himoyalangan (parolli) fayllar ochilmaydi

## 📄 Litsenziya

MIT — erkin ishlating, o'zgartiring, tarqating.
