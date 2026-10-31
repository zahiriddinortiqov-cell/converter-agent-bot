FROM python:3.12-slim

# LibreOffice (DOCX/XLSX/TXT -> PDF) + Tesseract OCR (uzb/rus/eng) + shriftlar
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer libreoffice-calc libreoffice-core \
    tesseract-ocr tesseract-ocr-uzb tesseract-ocr-rus tesseract-ocr-eng \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MODE=webhook PORT=8080
EXPOSE 8080

CMD ["python", "bot.py"]
