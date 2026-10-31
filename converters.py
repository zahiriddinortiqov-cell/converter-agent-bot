"""Konvertatsiya moduli: PDF, Word, rasmlar, OCR.

Formatlar:
  PDF  -> DOCX  (pdf2docx; matn bo'lmasa OCR ga tushadi)
  DOCX -> PDF   (LibreOffice headless)
  TXT  -> PDF   (LibreOffice headless)
  Rasm -> PDF / PNG / DOCX(OCR)  (Pillow + pytesseract)
"""
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

OCR_LANG = "uzb+rus+eng"  # tesseract til paketlari

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


class ConversionError(RuntimeError):
    pass


def _pdf_has_text(pdf_path: Path) -> bool:
    with fitz.open(pdf_path) as d:
        return any(page.get_text().strip() for page in d)


def pdf_to_docx_auto(pdf_path: Path, out_path: Path):
    """Matnli PDF -> pdf2docx; skanerlangan PDF -> OCR. (out_path, ocr_used) qaytaradi."""
    if _pdf_has_text(pdf_path):
        from pdf2docx import Converter
        cv = Converter(str(pdf_path))
        try:
            cv.convert(str(out_path))
        finally:
            cv.close()
        return out_path, False
    ocr_pdf_to_docx(pdf_path, out_path)
    return out_path, True


def ocr_pdf_to_docx(pdf_path: Path, out_path: Path):
    """Skanerlangan PDF: har bir sahifa rasmdan o'qib, Word hujjat yig'adi."""
    import io
    from docx import Document
    import pytesseract

    doc = Document()
    with fitz.open(pdf_path) as d:
        for i, page in enumerate(d):
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img, lang=OCR_LANG)
            if len(d) > 1:
                doc.add_heading(f"Sahifa {i + 1} / Page {i + 1}", level=2)
            for line in text.splitlines():
                doc.add_paragraph(line)
    if not out_path.parent.exists():
        out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return out_path


def ocr_image_to_docx(img_path: Path, out_path: Path):
    from docx import Document
    import pytesseract

    img = Image.open(img_path)
    text = pytesseract.image_to_string(img, lang=OCR_LANG)
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(str(out_path))
    return out_path


def _soffice() -> str:
    import shutil
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise ConversionError("LibreOffice topilmadi. Serverga: apt install libreoffice-writer")
    return soffice


def docx_to_pdf(docx_path: Path, out_path: Path):
    import subprocess
    r = subprocess.run(
        [_soffice(), "--headless", "--convert-to", "pdf",
         "--outdir", str(out_path.parent), str(docx_path)],
        capture_output=True, text=True, timeout=180,
    )
    produced = docx_path.with_suffix(".pdf")
    if r.returncode != 0 or not produced.exists():
        raise ConversionError(f"LibreOffice: {r.stderr[:300]}")
    if produced != out_path:
        produced.rename(out_path)
    return out_path


def txt_to_pdf(txt_path: Path, out_path: Path):
    return docx_to_pdf(txt_path, out_path)  # soffice txt->pdf ham qiladi


def image_convert(img_path: Path, out_path: Path, fmt: str):
    img = Image.open(img_path)
    if fmt.upper() in ("JPEG", "JPG"):
        img = img.convert("RGB")
    img.save(out_path, format=fmt)
    return out_path


def image_to_pdf(img_path: Path, out_path: Path):
    img = Image.open(img_path).convert("RGB")
    img.save(out_path, "PDF", resolution=150.0)
    return out_path
