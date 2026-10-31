"""3 tilli javoblar: o'zbek, rus, ingliz."""


def detect_lang(language_code: str | None) -> str:
    code = (language_code or "").lower()
    if code.startswith("uz"):
        return "uz"
    if code.startswith("ru"):
        return "ru"
    return "en"


STRINGS = {
    "uz": {
        "start": (
            "Salom! 👋 Men universal konvertor-agentman.\n\n"
            "📄 PDF → Word\n📝 Word → PDF\n"
            "🖼️ Rasm (JPG/PNG/WEBP) → PDF, Word (OCR) yoki boshqa rasm formati\n"
            "📃 Matn (TXT) → PDF\n\n"
            "Fayl yuboring — men formatni aniqlab, kerakli konvertatsiyani qilaman. "
            "Skanerlangan hujjatlar avtomatik OCR orqali o'qiladi."
        ),
        "converting": "Konvertatsiya qilinmoqda... ⏳",
        "done": "Tayyor! ✅",
        "ocr_used": "Matn OCR (optik tanib olish) orqali chiqarildi.",
        "choose_img": "Rasm uchun nima qilay?",
        "btn_pdf": "📄 PDF qilish",
        "btn_word_ocr": "📝 Word (matnni o'qib)",
        "btn_png": "🖼️ PNG qilish",
        "unsupported": "Bu formatni hali qo'llamayman. PDF, DOCX, JPG, PNG, WEBP, BMP, TIFF yoki TXT yuboring.",
        "error": "Xatolik yuz berdi: {err}\nFayl himoyalangan, buzilgan yoki juda murakkab bo'lishi mumkin.",
        "lang_set": "Til o'rnatildi: O'zbek 🇺🇿",
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
    },
    "ru": {
        "start": (
            "Привет! 👋 Я универсальный конвертор-агент.\n\n"
            "📄 PDF → Word\n📝 Word → PDF\n"
            "🖼️ Изображение (JPG/PNG/WEBP) → PDF, Word (OCR) или другой формат\n"
            "📃 Текст (TXT) → PDF\n\n"
            "Отправьте файл — я определю формат и выполню конвертацию. "
            "Сканированные документы читаются автоматически через OCR."
        ),
        "converting": "Конвертирую... ⏳",
        "done": "Готово! ✅",
        "ocr_used": "Текст извлечён через OCR (оптическое распознавание).",
        "choose_img": "Что сделать с изображением?",
        "btn_pdf": "📄 В PDF",
        "btn_word_ocr": "📝 В Word (распознать текст)",
        "btn_png": "🖼️ В PNG",
        "unsupported": "Этот формат пока не поддерживаю. Отправьте PDF, DOCX, JPG, PNG, WEBP, BMP, TIFF или TXT.",
        "error": "Произошла ошибка: {err}\nФайл может быть защищён, повреждён или слишком сложным.",
        "lang_set": "Язык установлен: Русский 🇷🇺",
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
    },
    "en": {
        "start": (
            "Hi! 👋 I'm a universal converter agent.\n\n"
            "📄 PDF → Word\n📝 Word → PDF\n"
            "🖼️ Image (JPG/PNG/WEBP) → PDF, Word (OCR) or another image format\n"
            "📃 Text (TXT) → PDF\n\n"
            "Send a file — I'll detect the format and convert it. "
            "Scanned documents are read automatically via OCR."
        ),
        "converting": "Converting... ⏳",
        "done": "Done! ✅",
        "ocr_used": "Text extracted via OCR (optical character recognition).",
        "choose_img": "What should I do with this image?",
        "btn_pdf": "📄 To PDF",
        "btn_word_ocr": "📝 To Word (read text)",
        "btn_png": "🖼️ To PNG",
        "unsupported": "I don't support this format yet. Send PDF, DOCX, JPG, PNG, WEBP, BMP, TIFF or TXT.",
        "error": "An error occurred: {err}\nThe file may be protected, corrupted or too complex.",
        "lang_set": "Language set: English 🇬🇧",
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    s = STRINGS.get(lang, STRINGS["en"]).get(key, key)
    return s.format(**kwargs) if kwargs else s
