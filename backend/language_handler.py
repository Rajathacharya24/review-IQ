"""
ReviewIQ — Multilingual Language Handler
Supports 15+ languages with robust detection, translation, and mixed-language handling.
"""

import re
from functools import lru_cache
from typing import List, Dict, Tuple, Any
from collections import Counter

from langdetect import detect, detect_langs, LangDetectException
from textblob import TextBlob
from deep_translator import GoogleTranslator
import langcodes

# ── Supported Languages ────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "zh-cn": "Chinese (Simplified)",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "ar": "Arabic",
}

# Language codes mapping
LANGDETECT_TO_ISO = {
    "en": "en",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
    "pt": "pt",
    "ru": "ru",
    "ja": "ja",
    "zh-cn": "zh-cn",
    "zh-tw": "zh-cn",
    "hi": "hi",
    "ta": "ta",
    "te": "te",
    "kn": "kn",
    "ml": "ml",
    "ar": "ar",
}


def _normalize_language_code(lang: str) -> str:
    """Convert language code to standard ISO format."""
    if lang in LANGDETECT_TO_ISO:
        return LANGDETECT_TO_ISO[lang]
    
    try:
        parsed = langcodes.parse(lang)
        code = parsed.to_alpha3()
        # Convert to 2-letter codes for common languages
        if code in ["eng"]: return "en"
        if code in ["spa"]: return "es"
        if code in ["fra"]: return "fr"
        if code in ["deu"]: return "de"
        if code in ["ita"]: return "it"
        if code in ["por"]: return "pt"
        if code in ["rus"]: return "ru"
        if code in ["jpn"]: return "ja"
        if code in ["zho"]: return "zh-cn"
        if code in ["hin"]: return "hi"
        if code in ["tam"]: return "ta"
        if code in ["tel"]: return "te"
        if code in ["kan"]: return "kn"
        if code in ["mal"]: return "ml"
        if code in ["ara"]: return "ar"
    except:
        pass
    
    return "en"


def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect language with confidence score.
    Returns: (language_code, confidence_score)
    """
    try:
        if len(text.strip()) < 3:
            return "en", 0.5
        
        # Try detecting with confidence
        detections = detect_langs(text)
        if detections:
            top_detection = detections[0]
            lang_code = _normalize_language_code(top_detection.lang)
            confidence = top_detection.prob
            return lang_code, confidence
        
        # Fallback to basic detect
        lang = detect(text)
        lang_code = _normalize_language_code(lang)
        return lang_code, 0.7
    
    except LangDetectException:
        return "en", 0.3
    except Exception:
        return "en", 0.3


def detect_mixed_languages(text: str) -> List[Dict[str, Any]]:
    """
    Detect if text contains multiple languages.
    Returns list of language segments with positions.
    """
    # Split by common punctuation but keep them
    sentences = re.split(r'([.!?;,])', text)
    
    detected_languages = []
    current_pos = 0
    
    for sentence in sentences:
        if not sentence.strip():
            current_pos += len(sentence)
            continue
        
        lang_code, confidence = detect_language(sentence)
        
        if detected_languages and detected_languages[-1]["lang"] == lang_code:
            # Extend the previous segment
            detected_languages[-1]["text"] += sentence
            detected_languages[-1]["end"] = current_pos + len(sentence)
        else:
            # New language segment
            detected_languages.append({
                "lang": lang_code,
                "text": sentence,
                "start": current_pos,
                "end": current_pos + len(sentence),
                "confidence": confidence
            })
        
        current_pos += len(sentence)
    
    return detected_languages


@lru_cache(maxsize=1000)
def translate_text(text: str, source_lang: str, target_lang: str = "en") -> str:
    """
    Translate text with fallback mechanisms.
    Cached to avoid redundant translations.
    """
    try:
        if source_lang == target_lang or source_lang == "en":
            return text
        
        # Use GoogleTranslator for reliable translation
        translator = GoogleTranslator(source_language=source_lang, target_language=target_lang)
        result = translator.translate(text)
        return result if result else text
    
    except Exception as e:
        # Fallback: Try to translate with 'auto' source
        try:
            translator = GoogleTranslator(source_language="auto", target_language=target_lang)
            result = translator.translate(text)
            return result if result else text
        except:
            # If translation fails, return original text
            return text


def translate_mixed_language_text(text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Translate mixed-language text to English.
    Returns: (translated_text, language_segments)
    """
    segments = detect_mixed_languages(text)
    
    # If only one language, simple translation
    if len(segments) <= 1:
        if segments:
            lang = segments[0]["lang"]
            translated = translate_text(text, lang, "en")
            return translated, segments
        return text, [{"lang": "en", "text": text, "confidence": 0.5}]
    
    # Multiple languages: translate each segment
    translated_parts = []
    for segment in segments:
        if segment["lang"] == "en":
            translated_parts.append(segment["text"])
        else:
            translated = translate_text(segment["text"], segment["lang"], "en")
            translated_parts.append(translated)
    
    translated_text = "".join(translated_parts)
    return translated_text, segments


def get_language_name(lang_code: str) -> str:
    """Get human-readable language name."""
    return SUPPORTED_LANGUAGES.get(lang_code, "Unknown")


def is_supported_language(lang_code: str) -> bool:
    """Check if language is supported."""
    return lang_code in SUPPORTED_LANGUAGES


def get_supported_languages() -> Dict[str, str]:
    """Get all supported languages."""
    return SUPPORTED_LANGUAGES.copy()


def detect_language_confidence(text: str) -> Dict[str, float]:
    """
    Get confidence scores for all detected languages.
    Returns dict of {language_code: confidence_score}
    """
    try:
        if len(text.strip()) < 3:
            return {"en": 0.5}
        
        detections = detect_langs(text)
        result = {}
        for detection in detections:
            lang_code = _normalize_language_code(detection.lang)
            result[lang_code] = detection.prob
        
        return result if result else {"en": 0.3}
    
    except:
        return {"en": 0.3}


def preprocess_multilingual_text(text: str) -> Dict[str, Any]:
    """
    Comprehensive preprocessing for multilingual text.
    Returns preprocessed data with language info.
    """
    # Detect language
    primary_lang, confidence = detect_language(text)
    
    # Detect mixed languages
    segments = detect_mixed_languages(text)
    has_mixed_languages = len(segments) > 1
    
    # Translate if needed
    if primary_lang != "en":
        translated_text, _ = translate_mixed_language_text(text)
    else:
        translated_text = text
    
    # Get all language detections
    lang_confidences = detect_language_confidence(text)
    
    return {
        "original_text": text,
        "translated_text": translated_text,
        "primary_language": primary_lang,
        "primary_confidence": confidence,
        "language_name": get_language_name(primary_lang),
        "has_mixed_languages": has_mixed_languages,
        "language_segments": segments,
        "all_language_confidences": lang_confidences,
        "is_supported": is_supported_language(primary_lang),
    }
