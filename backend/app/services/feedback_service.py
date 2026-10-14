from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate


def create_feedback(db: Session, feedback_in: FeedbackCreate) -> Feedback:
    """Persists a new feedback record in the database."""
    try:
        db_obj = Feedback(
            source=feedback_in.source,
            customer_identifier=feedback_in.customer_identifier,
            feedback_text=feedback_in.feedback_text,
            category=feedback_in.category,
            sentiment=feedback_in.sentiment,
            sentiment_score=feedback_in.sentiment_score,
            status="new",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception:
        db.rollback()
        raise


def get_feedback_by_id(db: Session, feedback_id: int) -> Optional[Feedback]:
    """Retrieves a single feedback record by primary key."""
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


def list_feedback(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    source: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc",
) -> Tuple[List[Feedback], int]:
    """Retrieves a paginated list of feedback records with optional filtering and sorting."""
    query = db.query(Feedback)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Feedback.feedback_text.ilike(search_term),
                Feedback.customer_identifier.ilike(search_term),
            )
        )

    if category and category.lower() != "all":
        query = query.filter(Feedback.category == category)

    if sentiment and sentiment.lower() != "all":
        query = query.filter(Feedback.sentiment == sentiment.lower())

    if source and source.lower() != "all":
        query = query.filter(Feedback.source == source)

    if status and status.lower() != "all":
        query = query.filter(Feedback.status == status.lower())

    total = query.count()

    sort_col_map = {
        "created_at": Feedback.created_at,
        "sentiment_score": Feedback.sentiment_score,
        "id": Feedback.id,
        "updated_at": Feedback.updated_at,
    }
    sort_column = sort_col_map.get(sort_by, Feedback.created_at)
    order_clause = sort_column.asc() if (order and order.lower() == "asc") else sort_column.desc()

    items = (
        query.order_by(order_clause)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total


def update_feedback(
    db: Session,
    feedback_id: int,
    feedback_in: FeedbackUpdate,
) -> Optional[Feedback]:
    """Updates an existing feedback record."""
    db_obj = get_feedback_by_id(db, feedback_id)
    if not db_obj:
        return None

    try:
        update_data = feedback_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception:
        db.rollback()
        raise


def delete_feedback(db: Session, feedback_id: int) -> bool:
    """Deletes a feedback record from the database."""
    db_obj = get_feedback_by_id(db, feedback_id)
    if not db_obj:
        return False

    try:
        db.delete(db_obj)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
