"""Universal Google Translate Engine for Helper-AI.

Provides universal translation across all 133+ Google Translate languages without requiring any API keys.
Supports UI translation, real-time agent thought translation, AI completion reply translation,
and local in-memory caching for sub-millisecond response times.
"""
import json
import logging
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger("GoogleTranslator")

# Comprehensive catalog of all official Google Translate languages (135+ languages)
SUPPORTED_LANGUAGES = [
    {"code": "af", "name": "Afrikaans", "native": "Afrikaans"},
    {"code": "ak", "name": "Twi", "native": "Twi"},
    {"code": "am", "name": "Amharic", "native": "አማርኛ"},
    {"code": "ar", "name": "Arabic", "native": "العربية"},
    {"code": "as", "name": "Assamese", "native": "অসমীয়া"},
    {"code": "ay", "name": "Aymara", "native": "Aymar aru"},
    {"code": "az", "name": "Azerbaijani", "native": "Azərbaycan"},
    {"code": "be", "name": "Belarusian", "native": "Беларуская"},
    {"code": "bg", "name": "Bulgarian", "native": "Български"},
    {"code": "bho", "name": "Bhojpuri", "native": "भोजपुरी"},
    {"code": "bm", "name": "Bambara", "native": "Bamanankan"},
    {"code": "bn", "name": "Bengali", "native": "বাংলা"},
    {"code": "bs", "name": "Bosnian", "native": "Bosanski"},
    {"code": "ca", "name": "Catalan", "native": "Català"},
    {"code": "ceb", "name": "Cebuano", "native": "Cebuano"},
    {"code": "ckb", "name": "Kurdish (Sorani)", "native": "کوردی سۆرانی"},
    {"code": "co", "name": "Corsican", "native": "Corsu"},
    {"code": "cs", "name": "Czech", "native": "Čeština"},
    {"code": "cy", "name": "Welsh", "native": "Cymraeg"},
    {"code": "da", "name": "Danish", "native": "Dansk"},
    {"code": "de", "name": "German", "native": "Deutsch"},
    {"code": "doi", "name": "Dogri", "native": "डोगरी"},
    {"code": "dv", "name": "Dhivehi", "native": "ދިވެހި"},
    {"code": "ee", "name": "Ewe", "native": "Eʋegbe"},
    {"code": "el", "name": "Greek", "native": "Ελληνικά"},
    {"code": "en", "name": "English", "native": "English"},
    {"code": "eo", "name": "Esperanto", "native": "Esperanto"},
    {"code": "es", "name": "Spanish", "native": "Español"},
    {"code": "et", "name": "Estonian", "native": "Eesti"},
    {"code": "eu", "name": "Basque", "native": "Euskara"},
    {"code": "fa", "name": "Persian", "native": "فارسی"},
    {"code": "fi", "name": "Finnish", "native": "Suomi"},
    {"code": "fil", "name": "Filipino", "native": "Filipino"},
    {"code": "fr", "name": "French", "native": "Français"},
    {"code": "fy", "name": "Frisian", "native": "Frysk"},
    {"code": "ga", "name": "Irish", "native": "Gaeilge"},
    {"code": "gd", "name": "Scots Gaelic", "native": "Gàidhlig"},
    {"code": "gl", "name": "Galician", "native": "Galego"},
    {"code": "gn", "name": "Guarani", "native": "Avañe'ẽ"},
    {"code": "gom", "name": "Konkani", "native": "कोंकणी"},
    {"code": "gu", "name": "Gujarati", "native": "ગુજરાતી"},
    {"code": "ha", "name": "Hausa", "native": "Hausa"},
    {"code": "haw", "name": "Hawaiian", "native": "ʻŌlelo Hawaiʻi"},
    {"code": "he", "name": "Hebrew", "native": "עברית"},
    {"code": "hi", "name": "Hindi", "native": "हिन्दी"},
    {"code": "hmn", "name": "Hmong", "native": "Hmoob"},
    {"code": "hr", "name": "Croatian", "native": "Hrvatski"},
    {"code": "ht", "name": "Haitian Creole", "native": "Kreyòl ayisyen"},
    {"code": "hu", "name": "Hungarian", "native": "Magyar"},
    {"code": "hy", "name": "Armenian", "native": "Հայերեն"},
    {"code": "id", "name": "Indonesian", "native": "Bahasa Indonesia"},
    {"code": "ig", "name": "Igbo", "native": "Igbo"},
    {"code": "ilo", "name": "Ilocano", "native": "Ilokano"},
    {"code": "is", "name": "Icelandic", "native": "Íslenska"},
    {"code": "it", "name": "Italian", "native": "Italiano"},
    {"code": "ja", "name": "Japanese", "native": "日本語"},
    {"code": "jw", "name": "Javanese", "native": "Basa Jawa"},
    {"code": "ka", "name": "Georgian", "native": "ქართული"},
    {"code": "kk", "name": "Kazakh", "native": "Қазақ тілі"},
    {"code": "km", "name": "Khmer", "native": "ភាសាខ្មែរ"},
    {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ"},
    {"code": "ko", "name": "Korean", "native": "한국어"},
    {"code": "kri", "name": "Krio", "native": "Krio"},
    {"code": "ku", "name": "Kurdish (Kurmanji)", "native": "Kurdî"},
    {"code": "ky", "name": "Kyrgyz", "native": "Кыргызча"},
    {"code": "la", "name": "Latin", "native": "Latina"},
    {"code": "lb", "name": "Luxembourgish", "native": "Lëtzebuergesch"},
    {"code": "lg", "name": "Luganda", "native": "Luganda"},
    {"code": "ln", "name": "Lingala", "native": "Lingála"},
    {"code": "lo", "name": "Lao", "native": "ລາວ"},
    {"code": "lt", "name": "Lithuanian", "native": "Lietuvių"},
    {"code": "lus", "name": "Mizo", "native": "Mizo ṭawng"},
    {"code": "lv", "name": "Latvian", "native": "Latviešu"},
    {"code": "mai", "name": "Maithili", "native": "मैथिली"},
    {"code": "mg", "name": "Malagasy", "native": "Malagasy"},
    {"code": "mi", "name": "Maori", "native": "Māori"},
    {"code": "mk", "name": "Macedonian", "native": "Македонски"},
    {"code": "ml", "name": "Malayalam", "native": "മലയാളം"},
    {"code": "mn", "name": "Mongolian", "native": "Монгол"},
    {"code": "mni-Mtei", "name": "Meiteilon (Manipuri)", "native": "মৈতৈলোন্"},
    {"code": "mr", "name": "Marathi", "native": "मराठी"},
    {"code": "ms", "name": "Malay", "native": "Bahasa Melayu"},
    {"code": "mt", "name": "Maltese", "native": "Malti"},
    {"code": "my", "name": "Burmese", "native": "မြန်မာ"},
    {"code": "ne", "name": "Nepali", "native": "नेपाली"},
    {"code": "nl", "name": "Dutch", "native": "Nederlands"},
    {"code": "no", "name": "Norwegian", "native": "Norsk"},
    {"code": "nso", "name": "Northern Sotho (Sepedi)", "native": "Sepedi"},
    {"code": "ny", "name": "Chichewa", "native": "Chichewa"},
    {"code": "om", "name": "Oromo", "native": "Afaan Oromoo"},
    {"code": "or", "name": "Odia", "native": "ଓଡ଼ିଆ"},
    {"code": "pa", "name": "Punjabi", "native": "ਪੰਜਾਬੀ"},
    {"code": "pl", "name": "Polish", "native": "Polski"},
    {"code": "ps", "name": "Pashto", "native": "پښتو"},
    {"code": "pt", "name": "Portuguese", "native": "Português"},
    {"code": "qu", "name": "Quechua", "native": "Runa Simi"},
    {"code": "ro", "name": "Romanian", "native": "Română"},
    {"code": "ru", "name": "Russian", "native": "Русский"},
    {"code": "rw", "name": "Kinyarwanda", "native": "Ikinyarwanda"},
    {"code": "sa", "name": "Sanskrit", "native": "संस्कृतम्"},
    {"code": "sd", "name": "Sindhi", "native": "سنڌي"},
    {"code": "si", "name": "Sinhala", "native": "සිංහල"},
    {"code": "sk", "name": "Slovak", "native": "Slovenčina"},
    {"code": "sl", "name": "Slovenian", "native": "Slovenščina"},
    {"code": "sm", "name": "Samoan", "native": "Gagana fa'a Sāmoa"},
    {"code": "sn", "name": "Shona", "native": "chiShona"},
    {"code": "so", "name": "Somali", "native": "Soomaaliga"},
    {"code": "sq", "name": "Albanian", "native": "Shqip"},
    {"code": "sr", "name": "Serbian", "native": "Српски"},
    {"code": "st", "name": "Sesotho", "native": "Sesotho"},
    {"code": "su", "name": "Sundanese", "native": "Basa Sunda"},
    {"code": "sv", "name": "Swedish", "native": "Svenska"},
    {"code": "sw", "name": "Swahili", "native": "Kiswahili"},
    {"code": "ta", "name": "Tamil", "native": "தமிழ்"},
    {"code": "te", "name": "Telugu", "native": "తెలుగు"},
    {"code": "tg", "name": "Tajik", "native": "Тоҷикӣ"},
    {"code": "th", "name": "Thai", "native": "ไทย"},
    {"code": "ti", "name": "Tigrinya", "native": "ትግርኛ"},
    {"code": "tk", "name": "Turkmen", "native": "Türkmençe"},
    {"code": "tr", "name": "Turkish", "native": "Türkçe"},
    {"code": "ts", "name": "Tsonga", "native": "Xitsonga"},
    {"code": "tt", "name": "Tatar", "native": "Татар теле"},
    {"code": "ug", "name": "Uyghur", "native": "ئۇيغۇرچە"},
    {"code": "uk", "name": "Ukrainian", "native": "Українська"},
    {"code": "ur", "name": "Urdu", "native": "اردو"},
    {"code": "uz", "name": "Uzbek", "native": "Oʻzbekcha"},
    {"code": "vi", "name": "Vietnamese", "native": "Tiếng Việt"},
    {"code": "xh", "name": "Xhosa", "native": "isiXhosa"},
    {"code": "yi", "name": "Yiddish", "native": "ייִדיש"},
    {"code": "yo", "name": "Yoruba", "native": "Èdè Yorùbá"},
    {"code": "zh-CN", "name": "Chinese (Simplified)", "native": "简体中文"},
    {"code": "zh-TW", "name": "Chinese (Traditional)", "native": "繁體中文"},
    {"code": "zu", "name": "Zulu", "native": "isiZulu"}
]


class GoogleTranslator:
    """Singleton universal translation engine with caching and fast fallbacks."""
    _instance: Optional["GoogleTranslator"] = None
    _cache: Dict[str, str] = {}

    @classmethod
    def get_instance(cls) -> "GoogleTranslator":
        if cls._instance is None:
            cls._instance = GoogleTranslator()
        return cls._instance

    def __init__(self):
        self._cache = {}

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Returns list of supported Google Translate languages."""
        return SUPPORTED_LANGUAGES

    def translate_text(self, text: str, target_lang: str = "en", source_lang: str = "auto") -> str:
        """
        Translates text to target_lang using Google Translate's universal client.
        Returns the original text if target_lang is 'en' and source is 'en', or if translation fails.
        """
        if not text or not str(text).strip():
            return text

        cleaned_text = str(text).strip()
        target_code = target_lang.lower().strip()
        source_code = source_lang.lower().strip()

        # If already matching target language, return directly
        if source_code == target_code or (source_code == "en" and target_code == "en"):
            return cleaned_text

        # Cache key lookup
        cache_key = f"{source_code}->{target_code}:{cleaned_text}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. Primary: Google Translate Mobile / Client endpoint (Zero API Key, High Availability)
        headers = {
            "User-Agent": "GoogleTranslate/6.28.0.05.421483610 (Linux; U; Android 12; Pixel 6)",
            "Accept": "*/*"
        }
        params = {
            "client": "gtx",
            "sl": source_code,
            "tl": target_code,
            "dt": "t",
            "q": cleaned_text
        }

        try:
            resp = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params=params,
                headers=headers,
                timeout=6
            )
            if resp.status_code == 200:
                parsed = resp.json()
                if parsed and isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], list):
                    segments = []
                    for part in parsed[0]:
                        if part and isinstance(part, list) and len(part) > 0 and part[0]:
                            segments.append(part[0])
                    translated_res = "".join(segments).strip()
                    if translated_res:
                        self._cache[cache_key] = translated_res
                        return translated_res
        except Exception as e:
            logger.debug(f"Google translate gtx request failed: {e}")

        # 2. Secondary fallback: Web Client translation query
        try:
            resp = requests.get(
                "https://clients5.google.com/translate_a/t",
                params={"client": "dict-chrome-ex", "sl": source_code, "tl": target_code, "q": cleaned_text},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
                    translated_res = data[0].strip()
                    if translated_res:
                        self._cache[cache_key] = translated_res
                        return translated_res
        except Exception as e:
            logger.debug(f"Google translate clients5 fallback failed: {e}")

        return cleaned_text

    def batch_translate(self, texts: List[str], target_lang: str, source_lang: str = "auto") -> List[str]:
        """Translates a list of texts sequentially or via cache."""
        return [self.translate_text(t, target_lang=target_lang, source_lang=source_lang) for t in texts]


translator = GoogleTranslator.get_instance()
