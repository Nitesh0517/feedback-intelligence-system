from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.feedback import Feedback
from app.processing.cleaner import clean_text, validate_text
from app.intelligence.sentiment_analyzer import get_sentiment_analyzer, SentimentResult
from app.intelligence.categorizer import get_categorizer, CategorizationResult
from app.core.logging import logger
from app.core.errors import NotFoundException, AppBaseException


@dataclass
class AnalysisResult:
    feedback_id: Optional[int]
    cleaned_text: str
    sentiment: str
    sentiment_score: float
    category: str
    status: str
    sentiment_details: Dict[str, Any]
    category_details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedback_id": self.feedback_id,
            "cleaned_text": self.cleaned_text,
            "sentiment": self.sentiment,
            "sentiment_score": round(self.sentiment_score, 4),
            "category": self.category,
            "status": self.status,
            "sentiment_details": self.sentiment_details,
            "category_details": self.category_details,
        }


def analyze_text(text: str, feedback_id: Optional[int] = None) -> AnalysisResult:
    """
    Performs pure text analysis (preprocessing, sentiment classification, categorization)
    without database side-effects.
    """
    cleaned = clean_text(text)
    
    sentiment_analyzer = get_sentiment_analyzer()
    sentiment_res: SentimentResult = sentiment_analyzer.analyze(cleaned)

    categorizer = get_categorizer()
    cat_res: CategorizationResult = categorizer.categorize(cleaned)

    return AnalysisResult(
        feedback_id=feedback_id,
        cleaned_text=cleaned,
        sentiment=sentiment_res.sentiment,
        sentiment_score=sentiment_res.confidence_score,
        category=cat_res.category,
        status="analyzed",
        sentiment_details=sentiment_res.to_dict(),
        category_details=cat_res.to_dict(),
    )


def analyze_and_update_feedback(db: Session, feedback_id: int) -> Feedback:
    """
    Retrieves feedback by ID, applies intelligence analysis pipeline, and updates
    the record atomically in PostgreSQL.
    """
    item = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not item:
        raise NotFoundException(f"Feedback with id {feedback_id} not found")

    try:
        analysis = analyze_text(item.feedback_text, feedback_id=item.id)

        # Update model fields
        item.sentiment = analysis.sentiment
        item.sentiment_score = analysis.sentiment_score
        item.category = analysis.category
        item.status = "analyzed"
        item.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(item)
        logger.info(
            f"Analyzed feedback id={item.id}: sentiment={item.sentiment} ({item.sentiment_score}), category='{item.category}'"
        )
        return item
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to analyze feedback id={feedback_id}: {str(e)}")
        if isinstance(e, AppBaseException):
            raise e
        raise AppBaseException(f"Analysis failed for feedback {feedback_id}: {str(e)}")


def batch_analyze_pending(db: Session, limit: int = 50) -> Dict[str, Any]:
    """
    Analyzes all feedback items with status='new' or unassigned sentiment up to limit.
    """
    query = db.query(Feedback).filter(
        (Feedback.status == "new") | (Feedback.sentiment.is_(None))
    ).limit(limit)

    items = query.all()
    analyzed_count = 0
    errors: List[Dict[str, Any]] = []

    for item in items:
        try:
            analysis = analyze_text(item.feedback_text, feedback_id=item.id)
            item.sentiment = analysis.sentiment
            item.sentiment_score = analysis.sentiment_score
            item.category = analysis.category
            item.status = "analyzed"
            item.updated_at = datetime.now(timezone.utc)
            analyzed_count += 1
        except Exception as e:
            errors.append({"id": item.id, "error": str(e)})

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Batch analysis commit error: {str(e)}")
        raise AppBaseException(f"Batch analysis database commit failed: {str(e)}")

    return {
        "processed_count": analyzed_count,
        "error_count": len(errors),
        "errors": errors,
    }
