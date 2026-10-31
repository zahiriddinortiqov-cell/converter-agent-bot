"""Konvertatsiya moduli: PDF, Word, Excel, rasmlar, matn, OCR.

PDF   -> DOCX / XLSX / PNG(zarurat bo'lsa ZIP) / TXT
DOCX  -> PDF / TXT / PNG
XLSX  -> PDF / PNG
TXT   -> PDF / DOCX
Rasm  -> PDF / PNG / DOCX(OCR)
"""
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

OCR_LANG = "uzb+rus+eng"
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


class ConversionError(RuntimeError):
    pass


# ---------- OCR ----------

def _ocr_pdf_pages(pdf_path: Path):
    import io
    import pytesseract

    with fitz.open(pdf_path) as d:
        for page in d:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            yield pytesseract.image_to_string(img, lang=OCR_LANG)


def _pdf_has_text(pdf_path: Path) -> bool:
    with fitz.open(pdf_path) as d:
        return any(page.get_text().strip() for page in d)


def pdf_to_docx_auto(pdf_path: Path, out_path: Path):
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
    from docx import Document

    doc = Document()
    pages = list(_ocr_pdf_pages(pdf_path))
    for i, text in enumerate(pages):
        if len(pages) > 1:
            doc.add_heading(f"Sahifa {i + 1} / Page {i + 1}", level=2)
        for line in text.splitlines():
            doc.add_paragraph(line)
    doc.save(str(out_path))
    return out_path


def pdf_to_txt_auto(pdf_path: Path, out_path: Path):
    texts = []
    with fitz.open(pdf_path) as d:
        for page in d:
            texts.append(page.get_text())
    ocr = False
    text = "\n\n".join(x for x in texts if x.strip()).strip()
    if not text:
        ocr = True
        text = "\n\n".join(p.strip() for p in _ocr_pdf_pages(pdf_path))
    out_path.write_text(text, encoding="utf-8")
    return out_path, ocr


def ocr_image_to_docx(img_path: Path, out_path: Path):
    import pytesseract
    from docx import Document

    img = Image.open(img_path)
    text = pytesseract.image_to_string(img, lang=OCR_LANG)
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(str(out_path))
    return out_path


# ---------- PDF -> rasm ----------

def pdf_to_png(pdf_path: Path, tmp: Path):
    """Sahifalarni PNG qiladi. 1 sahifa bo'lsa bitta PNG, ko'p bo'lsa ZIP."""
    import zipfile

    pages_dir = tmp / "pages"
    pages_dir.mkdir(exist_ok=True)
    paths = []
    with fitz.open(pdf_path) as d:
        for i, page in enumerate(d):
            p = pages_dir / f"page_{i + 1}.png"
            page.get_pixmap(dpi=150).save(str(p))
            paths.append(p)
    if len(paths) == 1:
        out = tmp / (Path(pdf_path).stem + ".png")
        paths[0].rename(out)
        return out, None
    out = tmp / (Path(pdf_path).stem + "_pages.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, arcname=p.name)
    return out, len(paths)


# ---------- PDF -> Excel ----------

def pdf_to_xlsx(pdf_path: Path, out_path: Path):
    """Jadvallarni pdfplumber orqali ajratib, openpyxl ga yozadi.
    Jadval topilmasa, matn qatorlari bir ustunga yoziladi."""
    import pdfplumber
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    tables = 0
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            for tbl in page.extract_tables() or []:
                tables += 1
                for row in tbl:
                    ws.append([("" if c is None else str(c)).strip() for c in row])
                ws.append([])
    if tables == 0:
        with fitz.open(pdf_path) as d:
            for page in d:
                for line in page.get_text().splitlines():
                    if line.strip():
                        ws.append([line.strip()])
    wb.save(str(out_path))
    return out_path


# ---------- LibreOffice orqali ... -> PDF ----------

def soffice_to_pdf(in_path: Path, out_path: Path):
    import shutil
    import subprocess

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise ConversionError("LibreOffice topilmadi")
    r = subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf",
         "--outdir", str(out_path.parent), str(in_path)],
        capture_output=True, text=True, timeout=180,
    )
    produced = in_path.with_suffix(".pdf")
    if r.returncode != 0 or not produced.exists():
        raise ConversionError(f"LibreOffice: {r.stderr[:300]}")
    if produced != out_path:
        produced.rename(out_path)
    return out_path


# ---------- Word <-> Matn ----------

def docx_to_txt(docx_path: Path, out_path: Path):
    from docx import Document

    doc = Document(str(docx_path))
    parts = [p.text for p in doc.paragraphs]
    for tbl in doc.tables:
        for row in tbl.rows:
            parts.append("\t".join(c.text for c in row.cells))
    out_path.write_text("\n".join(parts), encoding="utf-8")
    return out_path


def txt_to_docx(txt_path: Path, out_path: Path):
    from docx import Document

    doc = Document()
    for line in txt_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        doc.add_paragraph(line)
    doc.save(str(out_path))
    return out_path


# ---------- Rasmlar ----------

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
