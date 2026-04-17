"""
ReviewIQ — Multilingual Sentiment Analyzer
Advanced sentiment analysis for 15+ languages with context awareness.
"""

import re
import json
from typing import Dict, Any, List, Tuple
from functools import lru_cache

from textblob import TextBlob
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

from language_handler import detect_language, translate_text, SUPPORTED_LANGUAGES


# ── Multilingual Sentiment Words Database ──────────────────────────────────
MULTILINGUAL_SENTIMENT_KEYWORDS = {
    "en": {
        "positive": ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "perfect", "awesome", "outstanding"],
        "negative": ["bad", "terrible", "awful", "horrible", "hate", "poor", "useless", "waste", "disappointing", "broken"],
    },
    "es": {
        "positive": ["bueno", "excelente", "maravilloso", "fantástico", "amor", "perfecto", "asombroso", "genial"],
        "negative": ["malo", "terrible", "horribleble", "odio", "pobre", "inútil", "decepcionante", "roto"],
    },
    "fr": {
        "positive": ["bon", "excellent", "merveilleux", "fantastique", "amour", "parfait", "impressionnant", "magnifique"],
        "negative": ["mauvais", "terrible", "horrible", "odieux", "pauvre", "inutile", "décevant", "cassé"],
    },
    "de": {
        "positive": ["gut", "ausgezeichnet", "wunderbar", "fantastisch", "liebe", "perfekt", "beeindruckend", "großartig"],
        "negative": ["schlecht", "furchtbar", "schrecklich", "hasse", "arm", "nutzlos", "enttäuschend", "kaputt"],
    },
    "it": {
        "positive": ["buono", "eccellente", "meraviglioso", "fantastico", "amore", "perfetto", "impressionante", "magnifico"],
        "negative": ["cattivo", "terribile", "orribile", "odio", "povero", "inutile", "deludente", "rotto"],
    },
    "pt": {
        "positive": ["bom", "excelente", "maravilhoso", "fantástico", "amor", "perfeito", "impressionante", "magnífico"],
        "negative": ["ruim", "terrível", "horrível", "ódio", "pobre", "inútil", "decepcionante", "quebrado"],
    },
    "ru": {
        "positive": ["хороший", "отличный", "прекрасный", "фантастический", "любовь", "идеальный", "впечатляющий", "великолепный"],
        "negative": ["плохой", "ужасный", "страшный", "ненависть", "бедный", "бесполезный", "разочаровывающий", "сломанный"],
    },
    "ja": {
        "positive": ["良い", "素晴らしい", "完璧な", "素敵な", "愛", "優れた", "印象的な"],
        "negative": ["悪い", "ひどい", "嫌い", "不完全な", "つまらない", "壊れた"],
    },
    "hi": {
        "positive": ["अच्छा", "बेहतरीन", "शानदार", "बहुत अच्छा", "प्यार", "परफेक्ट", "आश्चर्यजनक"],
        "negative": ["बुरा", "भयानक", "गंभीर", "नफरत", "बुरा", "निरर्थक", "निराशाजनक"],
    },
    "ta": {
        "positive": ["நல்ல", "சிறந்த", "அद்भுத", "அழகான", "விருப்பம்", "சரிபெற்ற", "கண்ணிமைக்கத்தக்க"],
        "negative": ["கெட்ட", "பயங்கர", "கொடிய", "வெறுப்பு", "மோசமான", "பயனற்ற", "ஏமாற்றமான"],
    },
    "kn": {
        "positive": ["ಒಳ್ಳೆಯ", "ಅತ್ತೋತ್ತಮ", "ಅದ್ಭುತ", "ಸುಂದರ", "ಪ್ರೀತಿ", "ನಿಖುಂಜ", "ಆಶ್ಚರ್ಯಕರ"],
        "negative": ["ಕೆಟ್ಟ", "ಭೀಕರ", "ದೃಷ್ಟಾಂತವಿಲ್ಲದ", "ದ್ವೇಷ", "ಕ್ಷುದ್ರ", "ಬೇಕಾಗದ", "ನಿರಾಶಾಜನಕ"],
    },
}

# Feature keywords in multiple languages
FEATURE_KEYWORDS = {
    "battery_life": {
        "en": ["battery", "charge", "power", "charging", "endurance", "stamina"],
        "es": ["batería", "carga", "energía", "duración", "batería"],
        "fr": ["batterie", "charge", "puissance", "durée", "batterie"],
        "de": ["batterie", "ladung", "leistung", "dauer", "ausdauer"],
        "hi": ["बैटरी", "चार्ज", "ऊर्जा", "सहनशीलता"],
        "ta": ["பேட்டரி", "சார்ஜ்", "சக்தி", "நீடித்தன்மை"],
    },
    "build_quality": {
        "en": ["build", "quality", "material", "construction", "design", "durable"],
        "es": ["construcción", "calidad", "material", "diseño", "duradero"],
        "fr": ["construction", "qualité", "matériau", "conception", "durable"],
        "de": ["konstruktion", "qualität", "material", "design", "haltbar"],
        "hi": ["निर्माण", "गुणवत्ता", "सामग्री", "डिजाइन", "टिकाऊ"],
        "ta": ["கட்டமைப்பு", "தரம்", "பொருள்", "வடிவமைப்பு", "நீடித்த"],
    },
    "packaging": {
        "en": ["packaging", "box", "wrap", "unboxing", "presentation"],
        "es": ["embalaje", "caja", "envoltura", "desembalaje", "presentación"],
        "fr": ["emballage", "boîte", "enveloppe", "déballage", "présentation"],
        "de": ["verpackung", "karton", "verpackung", "auspacken", "präsentation"],
        "hi": ["पैकेजिंग", "बॉक्स", "लपेटना", "अनबॉक्सिंग", "प्रस्तुति"],
        "ta": ["பொதிதல்", "பெட்டி", "மடக்கு", "பெட்டி திறத்தல்", "முன்வைப்பு"],
    },
    "delivery_speed": {
        "en": ["delivery", "shipping", "fast", "quick", "delayed", "slow"],
        "es": ["entrega", "envío", "rápido", "lento", "retrasado"],
        "fr": ["livraison", "expédition", "rapide", "lent", "retardé"],
        "de": ["lieferung", "versand", "schnell", "langsam", "verspätet"],
        "hi": ["डिलीवरी", "शिपिंग", "तेज़", "धीमा", "विलंबित"],
        "ta": ["வழங்கல்", "கப்பல், விரைவு", "மெதுவான", "தாமதமான"],
    },
    "price_value": {
        "en": ["price", "cost", "value", "expensive", "cheap", "worth"],
        "es": ["precio", "costo", "valor", "caro", "barato", "vale"],
        "fr": ["prix", "coût", "valeur", "cher", "bon marché", "peine"],
        "de": ["preis", "kosten", "wert", "teuer", "billig", "wert"],
        "hi": ["कीमत", "लागत", "मूल्य", "महंगा", "सस्ता", "लायक"],
        "ta": ["விலை", "செலவு", "மதிப்பு", "விலையுயர்ந்த", "விலைக்குறைந்த", "சார்ந்த"],
    },
    "customer_support": {
        "en": ["support", "service", "customer", "help", "responsive"],
        "es": ["soporte", "servicio", "cliente", "ayuda", "responsivo"],
        "fr": ["support", "service", "client", "aide", "réactif"],
        "de": ["unterstützung", "dienst", "kunde", "hilfe", "reaktiv"],
        "hi": ["समर्थन", "सेवा", "ग्राहक", "मदद", "प्रतिक्रियाशील"],
        "ta": ["ஆதரவு", "சேவை", "வாहक", "உதவி", "செயலிகள்"],
    },
}


def _get_sentiment_keywords(language: str) -> Tuple[List[str], List[str]]:
    """Get positive and negative keywords for a language."""
    if language in MULTILINGUAL_SENTIMENT_KEYWORDS:
        keywords = MULTILINGUAL_SENTIMENT_KEYWORDS[language]
        return keywords.get("positive", []), keywords.get("negative", [])
    # Fallback to English
    keywords = MULTILINGUAL_SENTIMENT_KEYWORDS["en"]
    return keywords.get("positive", []), keywords.get("negative", [])


def keyword_based_sentiment(text: str, language: str) -> Tuple[str, float]:
    """
    Keyword-based sentiment analysis (fast fallback).
    Returns: (sentiment, confidence)
    """
    text_lower = text.lower()
    positive_keywords, negative_keywords = _get_sentiment_keywords(language)
    
    positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
    negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
    
    if positive_count == 0 and negative_count == 0:
        return "neutral", 0.3
    
    total = positive_count + negative_count
    positive_ratio = positive_count / total if total > 0 else 0
    
    if positive_ratio > 0.6:
        confidence = min(positive_count / max(total, 1), 1.0)
        return "positive", confidence
    elif positive_ratio < 0.4:
        confidence = min(negative_count / max(total, 1), 1.0)
        return "negative", confidence
    else:
        return "neutral", 0.5


def detect_sarcasm(text: str, language: str) -> Tuple[bool, float]:
    """
    Detect sarcasm indicators (heuristic-based).
    Returns: (is_sarcastic, confidence)
    """
    sarcasm_indicators = [
        r"!!+$",  # Multiple exclamation marks
        r"\?!+",  # Question with exclamation
        r"sure.*sure|yeah.*right|great.*not|love.*hate",  # Common sarcasm patterns
        r"so.*good|excellent.*not",
    ]
    
    text_lower = text.lower()
    indicator_count = sum(1 for pattern in sarcasm_indicators if re.search(pattern, text_lower))
    
    confidence = min(indicator_count / max(len(sarcasm_indicators), 1), 1.0)
    return indicator_count > 0, confidence


def extract_features_from_text(text: str, language: str) -> Dict[str, Dict[str, Any]]:
    """
    Extract feature sentiments from review text in any supported language.
    Returns dict of feature_name -> {sentiment, confidence, keywords_found}
    """
    text_lower = text.lower()
    features_analysis = {}
    
    for feature, lang_keywords in FEATURE_KEYWORDS.items():
        keywords = lang_keywords.get(language, lang_keywords.get("en", []))
        
        # Check if any keyword appears in text
        keywords_found = [kw for kw in keywords if kw in text_lower]
        
        if not keywords_found:
            features_analysis[feature] = {
                "sentiment": "not_mentioned",
                "confidence": 0.0,
                "keywords_found": [],
            }
            continue
        
        # Sentiment around keywords
        sentiment, confidence = keyword_based_sentiment(text, language)
        
        features_analysis[feature] = {
            "sentiment": sentiment,
            "confidence": confidence,
            "keywords_found": keywords_found,
        }
    
    return features_analysis


def comprehensive_sentiment_analysis(text: str, language: str) -> Dict[str, Any]:
    """
    Comprehensive sentiment analysis for multilingual text.
    """
    # Detect language if not provided
    if not language or language == "unknown":
        language, _ = detect_language(text)
    
    # Translate if needed
    if language != "en":
        translated_text = translate_text(text, language, "en")
    else:
        translated_text = text
    
    # Overall sentiment
    overall_sentiment, confidence = keyword_based_sentiment(translated_text, "en")
    
    # Sarcasm detection
    is_sarcastic, sarcasm_confidence = detect_sarcasm(translated_text, language)
    
    # Feature extraction
    features = extract_features_from_text(translated_text, "en")
    
    return {
        "overall_sentiment": overall_sentiment,
        "sentiment_confidence": confidence,
        "is_sarcastic": is_sarcastic,
        "sarcasm_confidence": sarcasm_confidence,
        "original_language": language,
        "translated_text": translated_text,
        "features": features,
    }
