import re
import unicodedata
from typing import Any, List, Dict


# Smart quotes and typography normalization mappings
UNICODE_REPLACEMENTS = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
    "\u00a0": " ",
}

# Regex to collapse multiple whitespace
WHITESPACE_REGEX = re.compile(r"\s+")

# Contraction-aware word tokenizer regex
TOKEN_REGEX = re.compile(r"\b[a-zA-Z0-9]+(?:'[a-zA-Z0-9]+)?\b")


def validate_text(text: Any, min_length: int = 1, max_length: int = 10000) -> str:
    """
    Validates input text.
    Raises ValueError if input is None, not a string, or outside valid length bounds.
    """
    if text is None:
        raise ValueError("Feedback text cannot be None.")
    if not isinstance(text, str):
        raise ValueError(f"Feedback text must be a string, got {type(text).__name__}.")
    
    cleaned = text.strip()
    if len(cleaned) < min_length:
        raise ValueError(f"Feedback text must contain at least {min_length} non-whitespace character(s).")
    if len(cleaned) > max_length:
        raise ValueError(f"Feedback text exceeds maximum length of {max_length} characters.")
        
    return cleaned


def normalize_unicode(text: str) -> str:
    """
    Normalizes Unicode representations (NFKC) and converts typographic quotes/dashes.
    """
    normalized = unicodedata.normalize("NFKC", text)
    for orig, repl in UNICODE_REPLACEMENTS.items():
        normalized = normalized.replace(orig, repl)
    return normalized


def normalize_whitespace(text: str) -> str:
    """
    Replaces sequences of tabs, carriage returns, and spaces with a single space.
    """
    return WHITESPACE_REGEX.sub(" ", text).strip()


def clean_text(text: Any) -> str:
    """
    Comprehensive text cleaning pipeline:
    1. Validates input.
    2. Performs Unicode NFKC and typographic normalization.
    3. Normalizes whitespace while preserving meaningful punctuation (.,!?-')
       and sentiment words (e.g., 'not', 'never', 'no').
    """
    validated = validate_text(text)
    unicode_clean = normalize_unicode(validated)
    return normalize_whitespace(unicode_clean)


def tokenize(text: str, lowercase: bool = True) -> List[str]:
    """
    Splits text into word tokens while preserving contractions (e.g. don't, wasn't).
    Negation words (not, never, no, cannot, neither, nor) are explicitly preserved.
    """
    cleaned = clean_text(text)
    if lowercase:
        cleaned = cleaned.lower()
    return TOKEN_REGEX.findall(cleaned)


def extract_features(text: str) -> Dict[str, Any]:
    """
    Extracts high-level statistical features and tokens from input text.
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned, lowercase=True)
    return {
        "cleaned_text": cleaned,
        "token_count": len(tokens),
        "char_count": len(cleaned),
        "tokens": tokens,
        "has_exclamation": "!" in cleaned,
        "has_question": "?" in cleaned,
    }
