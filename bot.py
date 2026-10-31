import asyncio
import os
import tempfile
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import converters as cv
from converters import IMG_EXTS
from i18n import detect_lang, t

BOT_TOKEN = os.getenv("BOT_TOKEN")
MODE = os.getenv("MODE", "polling")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
PORT = int(os.getenv("PORT", "8080"))
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USER_LANG: dict[int, str] = {}
PENDING: dict[int, tuple[str, str]] = {}  # user_id -> (file_id, file_name)

# Qaysi kiritilgan formatdan qaysi formatlar olish mumkin
CHOICES: dict[str, list[str]] = {
    ".pdf": ["docx", "xlsx", "png", "txt"],
    ".docx": ["pdf", "txt", "png"],
    ".xlsx": ["pdf", "png"],
    ".txt": ["pdf", "docx"],
}
IMG_CHOICES = ["pdf", "png", "docx_ocr"]

LABELS = {
    "docx": "📝 Word",
    "docx_ocr": "📝 Word (OCR)",
    "xlsx": "📊 Excel",
    "png": "🖼️ PNG (rasm)",
    "txt": "📃 TXT (matn)",
    "pdf": "📄 PDF",
}
EXT_OUT = {"docx": ".docx", "docx_ocr": ".docx", "xlsx": ".xlsx",
           "png": ".png", "txt": ".txt", "pdf": ".pdf"}


def lang_of(m: Message) -> str:
    uid = m.from_user.id
    if uid in USER_LANG:
        return USER_LANG[uid]
    return detect_lang(m.from_user.language_code if m.from_user else None)


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
    ]])


def choices_kb(ext: str) -> InlineKeyboardMarkup:
    fmts = IMG_CHOICES if ext in IMG_EXTS else CHOICES.get(ext, [])
    btns = [InlineKeyboardButton(text=LABELS[f], callback_data=f"conv:{f}") for f in fmts]
    return InlineKeyboardMarkup(inline_keyboard=[btns[i:i + 2] for i in range(0, len(btns), 2)])


# ---------- Til ----------

@dp.message(CommandStart())
async def start(m: Message):
    uid = m.from_user.id
    if uid not in USER_LANG:
        # Birinchi kirish: avval tilni so'raymiz
        await m.answer(t(detect_lang(m.from_user.language_code), "choose_lang"),
                       reply_markup=lang_kb())
    else:
        await m.answer(t(USER_LANG[uid], "start"))


@dp.message(Command("lang"))
async def lang_cmd(m: Message):
    await m.answer(t(lang_of(m), "choose_lang"), reply_markup=lang_kb())


@dp.callback_query(F.data.startswith("lang:"))
async def set_lang(c: CallbackQuery):
    code = c.data.split(":", 1)[1]
    USER_LANG[c.from_user.id] = code
    await c.message.edit_text(t(code, "start"))
    await c.answer()


# ---------- Fayl qabul qilish ----------

@dp.message(F.document)
async def handle_doc(m: Message):
    lang = lang_of(m)
    doc = m.document
    ext = Path(doc.file_name).suffix.lower()
    allowed = set(CHOICES) | IMG_EXTS
    if ext not in allowed:
        await m.answer(t(lang, "unsupported"))
        return
    PENDING[m.from_user.id] = (doc.file_id, doc.file_name)
    await m.answer(t(lang, "choose_format"), reply_markup=choices_kb(ext))


# ---------- Konvertatsiya ----------

def run_conversion(in_path: Path, ext: str, fmt: str, tmp: Path):
    out = tmp / (in_path.stem + EXT_OUT[fmt])
    flags = {"ocr": False, "zip_pages": None}
    if ext == ".pdf":
        if fmt == "docx":
            out, flags["ocr"] = cv.pdf_to_docx_auto(in_path, out)
        elif fmt == "txt":
            out, flags["ocr"] = cv.pdf_to_txt_auto(in_path, out)
        elif fmt == "png":
            out, flags["zip_pages"] = cv.pdf_to_png(in_path, tmp)
        elif fmt == "xlsx":
            out = cv.pdf_to_xlsx(in_path, out)
    elif ext in IMG_EXTS:
        if fmt == "pdf":
            out = cv.image_to_pdf(in_path, out)
        elif fmt == "png":
            out = cv.image_convert(in_path, out, "PNG")
        elif fmt == "docx_ocr":
            out = cv.ocr_image_to_docx(in_path, out)
            flags["ocr"] = True
    elif fmt == "pdf":
        out = cv.soffice_to_pdf(in_path, out)
    elif ext == ".docx" and fmt == "txt":
        out = cv.docx_to_txt(in_path, out)
    elif ext == ".txt" and fmt == "docx":
        out = cv.txt_to_docx(in_path, out)
    elif fmt == "png":  # docx/xlsx -> png (pdf orqali ikki bosqich)
        mid_pdf = cv.soffice_to_pdf(in_path, tmp / (in_path.stem + "_mid.pdf"))
        out, flags["zip_pages"] = cv.pdf_to_png(mid_pdf, tmp)
    else:
        raise cv.ConversionError("noto'g'ri format")
    return out, flags


@dp.callback_query(F.data.startswith("conv:"))
async def convert(c: CallbackQuery):
    lang = USER_LANG.get(c.from_user.id) or detect_lang(c.from_user.language_code)
    fmt = c.data.split(":", 1)[1]
    pending = PENDING.pop(c.from_user.id, None)
    if not pending:
        await c.answer(t(lang, "expired"), show_alert=True)
        return
    file_id, file_name = pending
    ext = Path(file_name).suffix.lower()
    status = await c.message.answer(t(lang, "converting"))
    try:
        f = await bot.get_file(file_id)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            in_path = tmp / file_name
            await bot.download_file(f.file_path, destination=in_path)
            out_path, flags = await asyncio.to_thread(run_conversion, in_path, ext, fmt, tmp)
            caption = t(lang, "done")
            if flags["ocr"]:
                caption += " " + t(lang, "ocr_used")
            if flags["zip_pages"]:
                caption += " " + t(lang, "zip_pages", n=flags["zip_pages"])
            await status.delete()
            await c.message.answer_document(FSInputFile(out_path), caption=caption)
    except Exception as e:
        await status.edit_text(t(lang, "error", err=type(e).__name__))
    await c.answer()


# ---------- Webhook / polling ----------

async def on_startup(bot: Bot):
    if MODE == "webhook":
        await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")


async def on_shutdown(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)


def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    if MODE == "polling":
        dp.run_polling(bot)
    else:
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
