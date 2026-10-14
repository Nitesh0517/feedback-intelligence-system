import pytest
from app.processing.cleaner import (
    validate_text,
    normalize_whitespace,
    normalize_unicode,
    clean_text,
    tokenize,
    extract_features,
)


def test_validate_text_valid():
    text = "Great customer service!"
    assert validate_text(text) == text


def test_validate_text_empty():
    with pytest.raises(ValueError, match="at least 1 non-whitespace"):
        validate_text("   ")

    with pytest.raises(ValueError, match="cannot be None"):
        validate_text(None)


def test_normalize_whitespace():
    raw = "This   is  a\n\ttest \r\nwith multiple    spaces."
    cleaned = normalize_whitespace(raw)
    assert cleaned == "This is a test with multiple spaces."


def test_normalize_unicode():
    raw = "“Antigravity’s—best…feature”"
    normalized = normalize_unicode(raw)
    assert normalized == '"Antigravity\'s-best...feature"'


def test_negation_preservation_in_tokenization():
    text = "The app did not work and was never fast, no matter what."
    tokens = tokenize(text, lowercase=True)
    assert "not" in tokens
    assert "never" in tokens
    assert "no" in tokens
    assert "did" in tokens


def test_contraction_tokenization():
    text = "Don't assume it can't handle high load."
    tokens = tokenize(text, lowercase=True)
    assert "don't" in tokens
    assert "can't" in tokens


def test_extract_features():
    text = "Is this fast?! Absolutely!"
    features = extract_features(text)
    assert features["token_count"] == 4
    assert features["has_exclamation"] is True
    assert features["has_question"] is True
    assert "fast" in features["tokens"]
