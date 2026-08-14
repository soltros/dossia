import re
import html
import logging
from typing import Tuple

logger = logging.getLogger("dossia.translator")

# Strict German function words
GERMAN_FUNCTION_WORDS = {
    "der", "die", "das", "und", "ist", "für", "nicht", "eine", "einen", "einem", "einer",
    "über", "kann", "können", "machen", "leserumfrage", "sicherheit", "datenschutz",
    "schützt", "deine", "privatsphäre", "warum", "oder", "sind", "mit", "nach", "bei",
    "auch", "durch", "werden", "wurde", "alle", "welche", "themen", "beiträge", "besser"
}

def is_strictly_foreign(text: str) -> Tuple[bool, str]:
    if not text or len(text.strip()) < 10:
        return False, "en"
    
    words = [w.lower() for w in re.findall(r'\b[a-zA-Zäöüßéèêàáíóúñç]+\b', text)]
    if not words:
        return False, "en"
    
    # Check German
    german_matches = sum(1 for w in words if w in GERMAN_FUNCTION_WORDS)
    has_umlauts = bool(re.search(r'[äöüßÄÖÜ]', text))
    
    # Require at least 2 German words or an umlaut + German word
    if german_matches >= 2 or (has_umlauts and german_matches >= 1):
        return True, "German"
        
    return False, "en"

def translate_to_english(text: str, max_chars: int = 2500) -> Tuple[str, bool, str]:
    """
    Detects if text is strictly foreign language and translates to clear English.
    Returns: (translated_text, was_translated, original_language)
    """
    if not text or len(text.strip()) < 5:
        return text, False, "en"
    
    is_foreign, lang_name = is_strictly_foreign(text)
    
    if not is_foreign:
        return text, False, "en"

    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target='en')
        
        snippet = text[:max_chars]
        translated = translator.translate(snippet)
        
        if translated and translated.strip().lower() != text.strip().lower():
            logger.info(f"Translated {lang_name} content: '{text[:40]}...' -> '{translated[:40]}...'")
            return translated, True, lang_name
    except Exception as e:
        logger.warning(f"Translation failed ({e}), using original text.")
        
    return text, False, "en"
