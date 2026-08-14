import re
import html
import logging
from typing import Tuple

logger = logging.getLogger("dossia.translator")

# Distinct German-only words (cannot be confused with English words like 'die' or 'mit')
DISTINCT_GERMAN_WORDS = {
    "leserumfrage", "datenschutz", "sicherheit", "schützt", "privatsphäre",
    "über", "können", "wurde", "nicht", "eine", "einen", "einem", "einer",
    "durch", "beiträge", "nachrichten", "einstellungen", "benutzer", "weiterlesen",
    "anmelden", "registrieren", "abonnieren", "umfrage", "kommentare", "archiv"
}

def is_strictly_foreign(text: str) -> Tuple[bool, str]:
    if not text or len(text.strip()) < 10:
        return False, "en"
    
    # If text contains standard English stopwords, verify it's not predominantly English
    english_stopwords = {"the", "and", "is", "in", "to", "of", "for", "with", "on", "at", "from", "by", "this", "that"}
    words_lower = [w.lower() for w in re.findall(r'\b[a-zA-Zäöüßéèêàáíóúñç]+\b', text)]
    
    eng_matches = sum(1 for w in words_lower if w in english_stopwords)
    if eng_matches >= 3 and not bool(re.search(r'[äöüßÄÖÜ]', text)):
        return False, "en"
    
    # Check German distinct words
    german_matches = sum(1 for w in words_lower if w in DISTINCT_GERMAN_WORDS)
    has_umlauts = bool(re.search(r'[äöüßÄÖÜ]', text))
    
    # Strictly require unambiguous German markers
    if (has_umlauts and german_matches >= 1) or german_matches >= 2:
        return True, "German"
    elif has_umlauts and len(words_lower) < 15:
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
