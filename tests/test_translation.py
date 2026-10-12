"""Unit tests for Universal Google Translation and API endpoints."""
import pytest
from core.translator import GoogleTranslator, SUPPORTED_LANGUAGES

def test_supported_languages_list():
    translator = GoogleTranslator.get_instance()
    langs = translator.get_supported_languages()
    assert len(langs) >= 100
    codes = [l["code"] for l in langs]
    assert "en" in codes
    assert "gu" in codes  # Gujarati
    assert "hi" in codes  # Hindi
    assert "es" in codes  # Spanish
    assert "fr" in codes  # French
    assert "de" in codes  # German
    assert "ja" in codes  # Japanese
    assert "ar" in codes  # Arabic

def test_translator_caching():
    translator = GoogleTranslator.get_instance()
    # Populate cache
    cache_key = "en->es:Hello"
    translator._cache[cache_key] = "Hola"
    res = translator.translate_text("Hello", target_lang="es", source_lang="en")
    assert res == "Hola"

def test_translator_same_language():
    translator = GoogleTranslator.get_instance()
    res = translator.translate_text("Hello world", target_lang="en", source_lang="en")
    assert res == "Hello world"

def test_translator_empty_text():
    translator = GoogleTranslator.get_instance()
    assert translator.translate_text("", target_lang="gu") == ""
    assert translator.translate_text(None, target_lang="gu") is None

def test_translator_batch():
    translator = GoogleTranslator.get_instance()
    translator._cache["auto->es:Apple"] = "Manzana"
    translator._cache["auto->es:Orange"] = "Naranja"
    res = translator.batch_translate(["Apple", "Orange"], target_lang="es")
    assert res == ["Manzana", "Naranja"]

def test_api_translate_endpoints():
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    
    # 1. Languages endpoint
    r_langs = client.get("/api/translate/languages")
    assert r_langs.status_code == 200
    data_langs = r_langs.json()
    assert "languages" in data_langs
    assert len(data_langs["languages"]) >= 100

    # 2. Translate single text
    r_single = client.post("/api/translate", json={
        "text": "Hello",
        "target_lang": "en"
    })
    assert r_single.status_code == 200
    assert r_single.json()["translated_text"] == "Hello"

    # 3. Translate batch texts
    r_batch = client.post("/api/translate", json={
        "texts": ["Hello", "World"],
        "target_lang": "en"
    })
    assert r_batch.status_code == 200
    assert r_batch.json()["translated_texts"] == ["Hello", "World"]
