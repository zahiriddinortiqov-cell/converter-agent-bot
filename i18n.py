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
            "📄 PDF → Word / Excel / Rasm / Matn\n"
            "📝 Word → PDF / Rasm / Matn\n"
            "📊 Excel → PDF\n"
            "🖼️ Rasm → PDF / PNG / Word (OCR)\n"
            "📃 Matn → PDF / Word\n\n"
            "Fayl yuboring — men qaysi format kerakligini so'rayman."
        ),
        "choose_lang": "Iltimos, tilni tanlang:",
        "choose_format": "Qaysi formatga o'tkazay? 👇",
        "converting": "Konvertatsiya qilinmoqda... ⏳",
        "done": "Tayyor! ✅",
        "ocr_used": "Matn OCR (optik tanib olish) orqali chiqarildi.",
        "zip_pages": "{n} ta sahifa rasm ZIP arxivida.",
        "expired": "Fayl muddati o'tgan, qaytadan yuboring.",
        "unsupported": "Bu formatni hali qo'llamayman. PDF, DOCX, XLSX, JPG, PNG, WEBP, BMP, TIFF yoki TXT yuboring.",
        "error": "Xatolik yuz berdi: {err}\nFayl himoyalangan, buzilgan yoki juda murakkab bo'lishi mumkin.",
        "lang_set": "Til o'rnatildi: O'zbek 🇺🇿",
    },
    "ru": {
        "start": (
            "Привет! 👋 Я универсальный конвертор-агент.\n\n"
            "📄 PDF → Word / Excel / Изображение / Текст\n"
            "📝 Word → PDF / Изображение / Текст\n"
            "📊 Excel → PDF\n"
            "🖼️ Изображение → PDF / PNG / Word (OCR)\n"
            "📃 Текст → PDF / Word\n\n"
            "Отправьте файл — я спрошу, в какой формат конвертировать."
        ),
        "choose_lang": "Пожалуйста, выберите язык:",
        "choose_format": "В какой формат конвертировать? 👇",
        "converting": "Конвертирую... ⏳",
        "done": "Готово! ✅",
        "ocr_used": "Текст извлечён через OCR (оптическое распознавание).",
        "zip_pages": "{n} страниц(ы) изображений в ZIP-архиве.",
        "expired": "Файл устарел, отправьте заново.",
        "unsupported": "Этот формат пока не поддерживаю. Отправьте PDF, DOCX, XLSX, JPG, PNG, WEBP, BMP, TIFF или TXT.",
        "error": "Произошла ошибка: {err}\nФайл может быть защищён, повреждён или слишком сложным.",
        "lang_set": "Язык установлен: Русский 🇷🇺",
    },
    "en": {
        "start": (
            "Hi! 👋 I'm a universal converter agent.\n\n"
            "📄 PDF → Word / Excel / Image / Text\n"
            "📝 Word → PDF / Image / Text\n"
            "📊 Excel → PDF\n"
            "🖼️ Image → PDF / PNG / Word (OCR)\n"
            "📃 Text → PDF / Word\n\n"
            "Send a file — I'll ask which format you need."
        ),
        "choose_lang": "Please choose a language:",
        "choose_format": "Which format should I convert to? 👇",
        "converting": "Converting... ⏳",
        "done": "Done! ✅",
        "ocr_used": "Text extracted via OCR (optical character recognition).",
        "zip_pages": "{n} page images in a ZIP archive.",
        "expired": "File expired, please send it again.",
        "unsupported": "I don't support this format yet. Send PDF, DOCX, XLSX, JPG, PNG, WEBP, BMP, TIFF or TXT.",
        "error": "An error occurred: {err}\nThe file may be protected, corrupted or too complex.",
        "lang_set": "Language set: English 🇬🇧",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    s = STRINGS.get(lang, STRINGS["en"]).get(key, key)
    return s.format(**kwargs) if kwargs else s
