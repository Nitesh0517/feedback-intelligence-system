from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional
from app.processing.cleaner import clean_text, tokenize
from app.core.config import settings
from app.core.logging import logger


@dataclass
class CategorizationResult:
    category: str
    confidence_score: float
    matched_features: List[str]
    category_scores: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "confidence_score": round(self.confidence_score, 4),
            "matched_features": self.matched_features,
            "category_scores": {k: round(v, 3) for k, v in self.category_scores.items()},
        }


# Multi-word phrase cues with strong category discriminative power (weight: 2.5)
CATEGORY_PHRASES: Dict[str, List[str]] = {
    "Product Quality": [
        "poor quality", "high quality", "defective item", "broken piece",
        "fell apart", "stopped working", "hardware issue", "hardware failure",
        "build quality", "poor craftsmanship", "material quality", "very durable",
    ],
    "Customer Support": [
        "customer service", "support team", "support agent", "help desk",
        "call center", "email response", "chat support", "support rep",
        "representative was", "no one replied", "spoke with", "spoke to support",
    ],
    "Pricing": [
        "too expensive", "worth the price", "value for money", "hidden fees",
        "subscription price", "overpriced for", "billing issue", "charged twice",
        "money back", "refund request", "price increase", "expensive for what",
    ],
    "Delivery": [
        "delivery time", "shipping delay", "arrived late", "package arrived",
        "lost package", "tracking number", "in transit", "on time delivery",
        "courier service", "damaged packaging", "late shipment", "dispatch delay",
    ],
    "User Experience": [
        "user experience", "user interface", "checkout flow", "easy to use",
        "hard to navigate", "confusing navigation", "app crashes", "web page",
        "cluttered layout", "login issue", "intuitive design", "clean ui",
    ],
    "Feature Request": [
        "please add", "would love to see", "feature request", "it would be great if",
        "can you add", "wish there was", "missing feature", "need an option to",
        "hope you add", "suggest adding", "dark mode support", "export option",
    ],
}

# Single keyword cues with moderate category discriminative power (weight: 1.0)
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Product Quality": [
        "quality", "durability", "durable", "defect", "defective",
        "broken", "malfunction", "flimsy", "sturdy", "craftsmanship",
        "broke", "tear", "torn", "wear", "hardware", "battery",
    ],
    "Customer Support": [
        "support", "agent", "representative", "rep", "ticket",
        "courteous", "unhelpful", "rude", "assistance", "assist",
        "advisor", "escalated", "reply",
    ],
    "Pricing": [
        "price", "pricing", "cost", "expensive", "cheap", "affordable",
        "billing", "subscription", "fee", "fees", "discount", "refund",
        "overpriced", "renewal", "charge", "charged", "invoice",
    ],
    "Delivery": [
        "delivery", "shipping", "shipped", "carrier", "package", "parcel",
        "courier", "dispatch", "arrival", "arrived", "tracking", "transit",
    ],
    "User Experience": [
        "ui", "ux", "interface", "navigation", "navigate", "intuitive",
        "confusing", "button", "layout", "website", "design", "usability",
        "cluttered", "click", "glitch", "screen",
    ],
    "Feature Request": [
        "feature", "suggest", "suggestion", "request", "requesting",
        "add", "wish", "missing", "option", "roadmap", "integrate", "integration",
    ],
}

VALID_CATEGORIES = [
    "Product Quality",
    "Customer Support",
    "Pricing",
    "Delivery",
    "User Experience",
    "Feature Request",
    "Other",
]


class BaseCategorizer:
    """Abstract base class for feedback categorizers."""
    def categorize(self, text: str) -> CategorizationResult:
        raise NotImplementedError


class BaselineCategorizer(BaseCategorizer):
    """
    Deterministic rule- and semantic keyword-based categorizer.
    Features:
    - Multi-word phrase matching with high priority weighting.
    - Word boundary keyword matching.
    - Softmax-like normalized confidence calculation.
    - Fallback to 'Other' when maximum category confidence is below threshold.
    """

    def __init__(self, threshold: Optional[float] = None):
        self.threshold = threshold if threshold is not None else settings.CLASSIFICATION_THRESHOLD

    def categorize(self, text: str) -> CategorizationResult:
        if not text or not isinstance(text, str) or not text.strip():
            return CategorizationResult(
                category="Other",
                confidence_score=0.50,
                matched_features=[],
                category_scores={c: 0.0 for c in VALID_CATEGORIES if c != "Other"},
            )

        cleaned = clean_text(text)
        lower_text = cleaned.lower()
        tokens = set(tokenize(lower_text, lowercase=True))

        scores: Dict[str, float] = {c: 0.0 for c in CATEGORY_KEYWORDS.keys()}
        matched_cues: Dict[str, List[str]] = {c: [] for c in CATEGORY_KEYWORDS.keys()}

        # 1. Match multi-word phrases (strong cue: +2.5 per match)
        for cat, phrases in CATEGORY_PHRASES.items():
            for phrase in phrases:
                if phrase in lower_text:
                    scores[cat] += 2.5
                    matched_cues[cat].append(phrase)

        # 2. Match individual keyword tokens (moderate cue: +1.0 per match)
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in tokens:
                    scores[cat] += 1.0
                    matched_cues[cat].append(kw)

        total_score = sum(scores.values())

        if total_score == 0:
            return CategorizationResult(
                category="Other",
                confidence_score=0.50,
                matched_features=[],
                category_scores=scores,
            )

        # Find category with highest weighted score
        best_cat, best_score = max(scores.items(), key=lambda item: item[1])

        # Confidence: proportion of evidence pointing to best category vs total matched evidence
        confidence = best_score / (total_score + 0.2)

        # If confidence or total evidence is too weak, fallback to "Other"
        if confidence < self.threshold or best_score < 1.0:
            assigned_category = "Other"
            final_confidence = 0.50
        else:
            assigned_category = best_cat
            final_confidence = min(0.98, max(0.55, confidence))

        return CategorizationResult(
            category=assigned_category,
            confidence_score=round(final_confidence, 4),
            matched_features=matched_cues.get(best_cat, []),
            category_scores=scores,
        )


def get_categorizer() -> BaseCategorizer:
    """Factory function returning the configured feedback categorizer."""
    return BaselineCategorizer()
