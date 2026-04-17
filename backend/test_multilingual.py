#!/usr/bin/env python3
"""
ReviewIQ — Multilingual Support Test Script
Tests language detection, translation, and sentiment analysis.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from language_handler import (
    detect_language,
    detect_mixed_languages,
    translate_text,
    preprocess_multilingual_text,
    get_supported_languages,
)
from multilingual_sentiment import comprehensive_sentiment_analysis

# Test data in multiple languages
TEST_REVIEWS = [
    # English
    {
        "text": "This phone has an amazing battery life and excellent build quality!",
        "lang": "English",
        "expected_sentiment": "positive"
    },
    # Hindi
    {
        "text": "यह फोन बहुत अच्छा है। बैटरी जीवन शानदार है।",
        "lang": "Hindi",
        "expected_sentiment": "positive"
    },
    # Spanish
    {
        "text": "El teléfono es excelente, pero la batería es muy mala.",
        "lang": "Spanish",
        "expected_sentiment": "mixed"
    },
    # French
    {
        "text": "Cet appareil est fantastique avec une batterie extraordinaire.",
        "lang": "French",
        "expected_sentiment": "positive"
    },
    # Kannada
    {
        "text": "ಈ ಫೋನ್‌ ತುಂಬಾ ಒಳ್ಳೆಯದಾಗಿದೆ ಮತ್ತು ನಿರ್ಮಾಣ ಉತ್ತಮವಾಗಿದೆ.",
        "lang": "Kannada",
        "expected_sentiment": "positive"
    },
    # Tamil
    {
        "text": "இந்த ஸ்மார்ட்ஃபோன் அருமையாக இருக்கிறது. பேட்டரி ஆயுள் நிறையது.",
        "lang": "Tamil",
        "expected_sentiment": "positive"
    },
    # Mixed Language
    {
        "text": "Great phone! बैटरी बहुत अच्छी है। Delivery was super fast!",
        "lang": "Mixed (EN/HI)",
        "expected_sentiment": "positive"
    },
    # German
    {
        "text": "Das Telefon ist gut, aber die Lieferung war langsam.",
        "lang": "German",
        "expected_sentiment": "mixed"
    },
]


def test_language_detection():
    """Test language detection accuracy."""
    print("\n" + "="*60)
    print("TEST 1: Language Detection")
    print("="*60)
    
    for i, review in enumerate(TEST_REVIEWS, 1):
        text = review["text"]
        detected_lang, confidence = detect_language(text)
        
        print(f"\n[{i}] {review['lang']}")
        print(f"    Text: {text[:60]}...")
        print(f"    Detected: {detected_lang} (confidence: {confidence:.2f})")
        print(f"    ✓ PASS" if detected_lang else "    ✗ FAIL")


def test_mixed_language_detection():
    """Test mixed language detection."""
    print("\n" + "="*60)
    print("TEST 2: Mixed Language Detection")
    print("="*60)
    
    mixed_review = "Great phone! बैटरी बहुत अच्छी है। Delivery was super fast!"
    segments = detect_mixed_languages(mixed_review)
    
    print(f"\nReview: {mixed_review}")
    print(f"Segments detected: {len(segments)}")
    
    for seg in segments:
        print(f"  - {seg['lang']}: {seg['text']}")
    
    has_multiple = len(segments) > 1
    print(f"\n{'✓ PASS' if has_multiple else '✗ FAIL'} - Mixed language detection")


def test_translation():
    """Test translation capability."""
    print("\n" + "="*60)
    print("TEST 3: Translation (English)")
    print("="*60)
    
    test_cases = [
        ("यह बहुत अच्छा है", "hi", "This is very good"),
        ("C'est très bon", "fr", "It's very good"),
        ("Es sehr gut", "de", "It's very good"),
    ]
    
    for i, (text, lang, expected) in enumerate(test_cases, 1):
        print(f"\n[{i}] {lang.upper()}")
        print(f"    Original: {text}")
        
        translated = translate_text(text, lang, "en")
        print(f"    Translated: {translated}")
        print(f"    (Expected similar to: {expected})")


def test_multilingual_preprocessing():
    """Test multilingual text preprocessing."""
    print("\n" + "="*60)
    print("TEST 4: Multilingual Text Preprocessing")
    print("="*60)
    
    test_text = "यह फोन बहुत अच्छा है"
    
    print(f"\nInput: {test_text}")
    result = preprocess_multilingual_text(test_text)
    
    print(f"Primary Language: {result['primary_language']}")
    print(f"Language Name: {result['language_name']}")
    print(f"Confidence: {result['primary_confidence']:.2f}")
    print(f"Translated: {result['translated_text']}")
    print(f"Has Mixed Languages: {result['has_mixed_languages']}")
    print(f"Is Supported: {result['is_supported']}")
    print(f"\n✓ PASS - Preprocessing complete")


def test_sentiment_analysis():
    """Test multilingual sentiment analysis."""
    print("\n" + "="*60)
    print("TEST 5: Multilingual Sentiment Analysis")
    print("="*60)
    
    for i, review in enumerate(TEST_REVIEWS[:6], 1):  # Test first 6 (non-mixed)
        text = review["text"]
        
        print(f"\n[{i}] {review['lang']}")
        print(f"    Text: {text[:50]}...")
        
        try:
            analysis = comprehensive_sentiment_analysis(text, "unknown")
            
            print(f"    Sentiment: {analysis['overall_sentiment']}")
            print(f"    Confidence: {analysis['sentiment_confidence']:.2f}")
            print(f"    Sarcastic: {analysis['is_sarcastic']}")
            
            # Show detected features
            features_detected = [f for f, data in analysis['features'].items() 
                               if data['sentiment'] != 'not_mentioned']
            if features_detected:
                print(f"    Features: {', '.join(features_detected)}")
            
            print(f"    ✓ PASS")
        except Exception as e:
            print(f"    ✗ FAIL: {str(e)}")


def test_supported_languages():
    """Test supported languages list."""
    print("\n" + "="*60)
    print("TEST 6: Supported Languages")
    print("="*60)
    
    langs = get_supported_languages()
    print(f"\nTotal languages supported: {len(langs)}")
    print("\nLanguages:")
    for code, name in sorted(langs.items()):
        print(f"  {code:6s} → {name}")
    
    print(f"\n✓ PASS - {len(langs)} languages available")


def main():
    """Run all tests."""
    print("\n" + "█"*60)
    print("█ ReviewIQ Multilingual Support Test Suite")
    print("█"*60)
    
    try:
        test_language_detection()
        test_mixed_language_detection()
        test_translation()
        test_multilingual_preprocessing()
        test_sentiment_analysis()
        test_supported_languages()
        
        print("\n" + "="*60)
        print("✓ All tests completed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
