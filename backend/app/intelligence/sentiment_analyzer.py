import math
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from app.processing.cleaner import clean_text, tokenize
from app.core.logging import logger


@dataclass
class SentimentResult:
    sentiment: str  # "positive", "negative", or "neutral"
    confidence_score: float  # Calibrated score in range [0.0, 1.0]
    compound_score: float  # Normalized polarity between [-1.0, 1.0]
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sentiment": self.sentiment,
            "confidence_score": round(self.confidence_score, 4),
            "compound_score": round(self.compound_score, 4),
            "details": self.details,
        }


# Curated sentiment lexicon with valence ratings (-3.0 to +3.0)
SENTIMENT_LEXICON: Dict[str, float] = {
    # Strong positive (+2.5 to +3.0)
    "excellent": 2.8,
    "outstanding": 2.9,
    "exceptional": 3.0,
    "fantastic": 2.7,
    "superb": 2.8,
    "brilliant": 2.6,
    "perfect": 3.0,
    "amazing": 2.7,
    "wonderful": 2.6,
    "flawless": 2.8,
    "delighted": 2.5,
    "love": 2.5,
    "loved": 2.5,
    
    # Moderate positive (+1.2 to +2.4)
    "great": 2.0,
    "good": 1.5,
    "nice": 1.4,
    "pleasant": 1.5,
    "happy": 1.8,
    "satisfied": 1.7,
    "helpful": 1.6,
    "fast": 1.5,
    "quick": 1.4,
    "smooth": 1.6,
    "intuitive": 1.8,
    "reliable": 1.8,
    "clean": 1.3,
    "responsive": 1.7,
    "recommend": 1.9,
    "prompt": 1.6,
    "effective": 1.7,
    "efficient": 1.8,
    "affordable": 1.5,
    "valuable": 1.7,
    "seamless": 2.0,
    
    # Strong negative (-2.5 to -3.0)
    "terrible": -2.8,
    "horrible": -2.9,
    "awful": -2.8,
    "abysmal": -3.0,
    "disaster": -2.9,
    "disastrous": -2.9,
    "unusable": -2.8,
    "garbage": -2.7,
    "trash": -2.6,
    "worst": -3.0,
    "scam": -3.0,
    "hate": -2.5,
    "hated": -2.5,

    # Moderate negative (-1.2 to -2.4)
    "bad": -1.5,
    "poor": -1.8,
    "broken": -2.2,
    "crash": -2.1,
    "crashed": -2.1,
    "crashes": -2.1,
    "bug": -1.7,
    "buggy": -2.0,
    "slow": -1.6,
    "sluggish": -1.8,
    "lag": -1.5,
    "laggy": -1.7,
    "expensive": -1.4,
    "overpriced": -1.8,
    "rude": -2.2,
    "unhelpful": -2.0,
    "delayed": -1.8,
    "delay": -1.6,
    "disappointed": -2.2,
    "disappointing": -2.2,
    "frustrated": -2.0,
    "frustrating": -2.0,
    "annoying": -1.7,
    "useless": -2.4,
    "failed": -2.0,
    "fail": -1.8,
    "error": -1.6,
    "errors": -1.6,
    "refund": -1.5,
}

# Negation words that invert subsequent word polarity
NEGATION_WORDS = {
    "not", "never", "no", "neither", "nor", "none", "cannot",
    "can't", "cant", "won't", "wont", "don't", "dont", "didn't",
    "didnt", "isn't", "isnt", "wasn't", "wasnt", "hardly", "barely",
}

# Intensifiers and diminishers
INTENSIFIERS: Dict[str, float] = {
    "very": 1.4,
    "extremely": 1.6,
    "incredibly": 1.6,
    "really": 1.3,
    "super": 1.4,
    "absolutely": 1.5,
    "completely": 1.4,
    "totally": 1.4,
    "slightly": 0.6,
    "somewhat": 0.7,
    "a bit": 0.7,
}


class BaseSentimentAnalyzer:
    """Abstract base class for replaceable sentiment classification models."""
    def analyze(self, text: str) -> SentimentResult:
        raise NotImplementedError


class BaselineSentimentAnalyzer(BaseSentimentAnalyzer):
    """
    Transparent, deterministic baseline sentiment analyzer.
    Features:
    - Domain polarity dictionary scoring.
    - Negation handling within a 3-token lookbehind window.
    - Intensifier scaling (e.g. 'extremely good' vs 'slightly good').
    - Compound polarity normalized mathematically via hyperbolic normalization.
    - Calibrated confidence calculation reflecting linguistic signal strength.
    """

    def __init__(self, neutral_threshold: float = 0.15):
        self.neutral_threshold = neutral_threshold

    def analyze(self, text: str) -> SentimentResult:
        if not text or not isinstance(text, str) or not text.strip():
            return SentimentResult(
                sentiment="neutral",
                confidence_score=0.50,
                compound_score=0.0,
                details={"reason": "empty_or_whitespace_input"},
            )

        cleaned = clean_text(text)
        tokens = tokenize(cleaned, lowercase=True)

        if not tokens:
            return SentimentResult(
                sentiment="neutral",
                confidence_score=0.50,
                compound_score=0.0,
                details={"reason": "no_alphanumeric_tokens"},
            )

        scores: List[float] = []
        matched_words: List[str] = []

        for i, token in enumerate(tokens):
            if token in SENTIMENT_LEXICON:
                valence = SENTIMENT_LEXICON[token]

                # Check lookbehind window for intensifiers & negations
                window_start = max(0, i - 3)
                window = tokens[window_start:i]

                # Intensifier check
                for prev in window:
                    if prev in INTENSIFIERS:
                        valence *= INTENSIFIERS[prev]

                # Negation check: if an odd count of negations is in window, invert valence
                negation_count = sum(1 for prev in window if prev in NEGATION_WORDS)
                if negation_count % 2 == 1:
                    valence = -valence * 0.85  # Invert and slightly dampen

                scores.append(valence)
                matched_words.append(token)

        total_valence = sum(scores)

        # Normalize score into [-1.0, 1.0] using hyperbolic scaling: total / sqrt(total^2 + 15)
        if total_valence != 0:
            compound = total_valence / math.sqrt(total_valence**2 + 15.0)
        else:
            compound = 0.0

        # Punctuation bonus: multiple exclamation points slightly amplify polarity
        exclamation_count = text.count("!")
        if exclamation_count > 0 and compound != 0:
            boost = min(0.15, exclamation_count * 0.05)
            compound = max(-1.0, min(1.0, compound + (boost if compound > 0 else -boost)))

        # Determine sentiment class and calibrated confidence score
        if compound >= self.neutral_threshold:
            sentiment = "positive"
            # Calibrated confidence: increases with polarity magnitude and matched terms
            confidence = min(0.99, max(0.55, 0.50 + abs(compound) * 0.45 + min(0.1, len(matched_words) * 0.02)))
        elif compound <= -self.neutral_threshold:
            sentiment = "negative"
            confidence = min(0.99, max(0.55, 0.50 + abs(compound) * 0.45 + min(0.1, len(matched_words) * 0.02)))
        else:
            sentiment = "neutral"
            # In neutral zone, confidence is highest when compound is near 0.0 and no polar words exist
            if len(matched_words) == 0:
                confidence = 0.80
            else:
                confidence = min(0.75, max(0.50, 0.75 - abs(compound)))

        return SentimentResult(
            sentiment=sentiment,
            confidence_score=round(confidence, 4),
            compound_score=round(compound, 4),
            details={
                "matched_terms": matched_words,
                "lexicon_valence_sum": round(total_valence, 3),
                "token_count": len(tokens),
            },
        )


def get_sentiment_analyzer() -> BaseSentimentAnalyzer:
    """
    Factory function returning the configured sentiment analyzer.
    Easily pluggable with transformer or ML models based on environment settings.
    """
    return BaselineSentimentAnalyzer()
