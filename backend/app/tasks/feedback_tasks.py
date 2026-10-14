from datetime import datetime, timezone
from typing import Dict, Any, Optional
from celery import shared_task

from app.tasks.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.feedback import Feedback
from app.services.feedback_analysis_service import analyze_text, batch_analyze_pending
from app.core.logging import logger


@celery_app.task(bind=True, name="tasks.analyze_feedback_task")
def analyze_feedback_task(self, feedback_id: int) -> Dict[str, Any]:
    """
    Asynchronous Celery task to analyze sentiment and category of a feedback item.
    Safely manages database sessions, prevents duplicate processing, and updates DB.
    """
    task_id = self.request.id
    logger.info(f"[Task {task_id}] Starting async analysis for feedback_id={feedback_id}")

    db = SessionLocal()
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            logger.warning(f"[Task {task_id}] Feedback ID {feedback_id} not found in database.")
            return {
                "task_id": task_id,
                "feedback_id": feedback_id,
                "status": "failed",
                "error": f"Feedback ID {feedback_id} not found",
            }

        # Check for duplicate processing
        if feedback.status == "analyzed" and feedback.sentiment is not None:
            logger.info(f"[Task {task_id}] Feedback {feedback_id} was already analyzed; skipping duplicate execution.")
            return {
                "task_id": task_id,
                "feedback_id": feedback.id,
                "status": "completed",
                "sentiment": feedback.sentiment,
                "sentiment_score": feedback.sentiment_score,
                "category": feedback.category,
                "note": "already_analyzed",
            }

        # Perform NLP analysis
        analysis = analyze_text(feedback.feedback_text, feedback_id=feedback.id)

        # Update database record
        feedback.sentiment = analysis.sentiment
        feedback.sentiment_score = analysis.sentiment_score
        feedback.category = analysis.category
        feedback.status = "analyzed"
        feedback.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(feedback)

        logger.info(
            f"[Task {task_id}] Completed analysis for feedback_id={feedback_id}: "
            f"sentiment={feedback.sentiment} ({feedback.sentiment_score}), category='{feedback.category}'"
        )

        return {
            "task_id": task_id,
            "feedback_id": feedback.id,
            "status": "completed",
            "sentiment": feedback.sentiment,
            "sentiment_score": feedback.sentiment_score,
            "category": feedback.category,
        }

    except Exception as exc:
        db.rollback()
        logger.error(f"[Task {task_id}] Error analyzing feedback_id={feedback_id}: {str(exc)}", exc_info=True)
        return {
            "task_id": task_id,
            "feedback_id": feedback_id,
            "status": "failed",
            "error": str(exc),
        }
    finally:
        db.close()


@celery_app.task(bind=True, name="tasks.batch_analyze_feedback_task")
def batch_analyze_feedback_task(self, limit: int = 50) -> Dict[str, Any]:
    """
    Asynchronous Celery task to batch process pending/unanalyzed feedback items.
    """
    task_id = self.request.id
    logger.info(f"[Task {task_id}] Starting batch analysis for up to {limit} pending feedback items")

    db = SessionLocal()
    try:
        results = batch_analyze_pending(db=db, limit=limit)
        logger.info(
            f"[Task {task_id}] Batch analysis complete: processed={results.get('processed_count')}, "
            f"errors={results.get('error_count')}"
        )
        return {
            "task_id": task_id,
            "status": "completed",
            "processed_count": results.get("processed_count", 0),
            "error_count": results.get("error_count", 0),
            "errors": results.get("errors", []),
        }
    except Exception as exc:
        db.rollback()
        logger.error(f"[Task {task_id}] Batch analysis error: {str(exc)}", exc_info=True)
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(exc),
        }
    finally:
        db.close()
