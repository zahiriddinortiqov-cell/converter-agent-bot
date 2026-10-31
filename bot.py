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

from converters import (IMG_EXTS, ConversionError, docx_to_pdf, image_convert,
                          image_to_pdf, ocr_image_to_docx, pdf_to_docx_auto,
                          txt_to_pdf)
from i18n import STRINGS, detect_lang, t

BOT_TOKEN = os.getenv("BOT_TOKEN")
MODE = os.getenv("MODE", "polling")            # polling | webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")       # https://sizning-domen.uz
PORT = int(os.getenv("PORT", "8080"))
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USER_LANG: dict[int, str] = {}
PENDING_IMG: dict[int, tuple[str, str]] = {}  # user_id -> (file_id, file_name)


def lang_of(m: Message) -> str:
    if m.from_user and m.from_user.id in USER_LANG:
        return USER_LANG[m.from_user.id]
    return detect_lang(m.from_user.language_code if m.from_user else None)


@dp.message(CommandStart())
async def start(m: Message):
    await m.answer(t(lang_of(m), "start"))


@dp.message(Command("lang"))
async def choose_lang(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
    ]])
    await m.answer(t(lang_of(m), "choose_lang"), reply_markup=kb)


@dp.callback_query(F.data.startswith("lang:"))
async def set_lang(c: CallbackQuery):
    code = c.data.split(":", 1)[1]
    USER_LANG[c.from_user.id] = code
    await c.message.edit_text(t(code, "lang_set"))
    await c.answer()


async def download(doc, tmp: Path) -> Path:
    p = tmp / doc.file_name
    await bot.download(doc, destination=p)
    return p


async def send_result(m: Message, out_path: Path, lang: str, ocr_used: bool = False):
    caption = t(lang, "done")
    if ocr_used:
        caption += " " + t(lang, "ocr_used")
    await m.answer_document(FSInputFile(out_path), caption=caption)


@dp.message(F.document)
async def handle_doc(m: Message):
    lang = lang_of(m)
    doc = m.document
    ext = Path(doc.file_name).suffix.lower()

    if ext not in IMG_EXTS | {".pdf", ".docx", ".txt"}:
        await m.answer(t(lang, "unsupported"))
        return

    if ext in IMG_EXTS:
        PENDING_IMG[m.from_user.id] = (doc.file_id, doc.file_name)
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=t(lang, "btn_pdf"), callback_data="img:pdf"),
            InlineKeyboardButton(text=t(lang, "btn_word_ocr"), callback_data="img:docx"),
            InlineKeyboardButton(text=t(lang, "btn_png"), callback_data="img:png"),
        ]])
        await m.answer(t(lang, "choose_img"), reply_markup=kb)
        return

    status = await m.answer(t(lang, "converting"))
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        try:
            in_path = await download(doc, tmp)
            if ext == ".pdf":
                out_path, ocr_used = await asyncio.to_thread(
                    pdf_to_docx_auto, in_path, tmp / (in_path.stem + ".docx"))
            elif ext == ".docx":
                out_path = await asyncio.to_thread(
                    docx_to_pdf, in_path, tmp / (in_path.stem + ".pdf"))
                ocr_used = False
            else:  # .txt
                out_path = await asyncio.to_thread(
                    txt_to_pdf, in_path, tmp / (in_path.stem + ".pdf"))
                ocr_used = False
            await status.delete()
            await send_result(m, out_path, lang, ocr_used)
        except (ConversionError, Exception) as e:
            await status.edit_text(t(lang, "error", err=type(e).__name__))


@dp.callback_query(F.data.startswith("img:"))
async def handle_img_choice(c: CallbackQuery):
    lang = detect_lang(c.from_user.language_code)
    if c.from_user.id in USER_LANG:
        lang = USER_LANG[c.from_user.id]
    action = c.data.split(":", 1)[1]
    pending = PENDING_IMG.pop(c.from_user.id, None)
    if not pending:
        await c.answer("File eski", show_alert=True)
        return

    file_id, file_name = pending
    ext_map = {"pdf": ".pdf", "docx": ".docx", "png": ".png"}
    out_ext = ext_map[action]
    status = await c.message.answer(t(lang, "converting"))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        try:
            f = await bot.get_file(file_id)
            in_path = tmp / file_name
            await bot.download_file(f.file_path, destination=in_path)
            out_path = tmp / (Path(file_name).stem + out_ext)

            def job():
                if action == "pdf":
                    return image_to_pdf(in_path, out_path), False
                if action == "docx":
                    return ocr_image_to_docx(in_path, out_path), True
                return image_convert(in_path, out_path, "PNG"), False

            out_path, ocr_used = await asyncio.to_thread(job)
            await status.delete()
            await send_result(c.message, out_path, lang, ocr_used)
        except Exception as e:
            await status.edit_text(t(lang, "error", err=type(e).__name__))
    await c.answer()


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
