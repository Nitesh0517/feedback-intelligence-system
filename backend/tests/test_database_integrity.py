from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.feedback import Feedback
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate
from app.services import feedback_service, user_service


def test_feedback_sentiment_score_check_constraint(db_session):
    """Verifies that database CheckConstraint rejects sentiment_score out of [0.0, 1.0]."""
    # Negative score
    invalid_feedback = Feedback(
        source="Web",
        feedback_text="Testing negative constraint",
        sentiment="negative",
        sentiment_score=-0.5,
        status="new",
    )
    db_session.add(invalid_feedback)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Score > 1.0
    invalid_feedback2 = Feedback(
        source="Web",
        feedback_text="Testing overflow constraint",
        sentiment="positive",
        sentiment_score=1.5,
        status="new",
    )
    db_session.add(invalid_feedback2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_user_role_check_constraint(db_session):
    """Verifies that database CheckConstraint rejects invalid user roles."""
    invalid_user = User(
        name="Invalid Role User",
        email="invalid_role@example.com",
        hashed_password="somehashedpassword",
        role="superuser",  # Only 'admin', 'analyst', 'viewer' allowed
        is_active=True,
    )
    db_session.add(invalid_user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_user_unique_email_constraint(db_session):
    """Verifies that database prevents duplicate user emails."""
    u1 = User(
        name="User One",
        email="unique@example.com",
        hashed_password="hash1",
        role="viewer",
        is_active=True,
    )
    db_session.add(u1)
    db_session.commit()

    u2 = User(
        name="User Two",
        email="unique@example.com",
        hashed_password="hash2",
        role="analyst",
        is_active=True,
    )
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_transaction_rollback_on_failure(db_session):
    """Verifies that service functions roll back cleanly when a database operation fails."""
    # Attempt to create an invalid feedback with out-of-range sentiment score
    with pytest.raises(Exception):
        feedback_service.create_feedback(
            db=db_session,
            feedback_in=FeedbackCreate(
                source="API",
                feedback_text="Will fail constraint",
                sentiment_score=2.0,  # invalid
            ),
        )

    # Confirm session is usable and no corrupted record was committed
    records = db_session.query(Feedback).filter(Feedback.feedback_text == "Will fail constraint").all()
    assert len(records) == 0


def test_feedback_sorting_queries(db_session):
    """Verifies sorting capabilities of list_feedback by created_at and sentiment_score."""
    base_time = datetime.now(timezone.utc)
    f1 = Feedback(
        source="Web",
        feedback_text="First low score",
        sentiment="negative",
        sentiment_score=0.1,
        status="new",
        created_at=base_time - timedelta(days=2),
    )
    f2 = Feedback(
        source="App",
        feedback_text="Second medium score",
        sentiment="neutral",
        sentiment_score=0.5,
        status="new",
        created_at=base_time - timedelta(days=1),
    )
    f3 = Feedback(
        source="Survey",
        feedback_text="Third high score",
        sentiment="positive",
        sentiment_score=0.9,
        status="new",
        created_at=base_time,
    )
    db_session.add_all([f1, f2, f3])
    db_session.commit()

    # Sort by sentiment_score ASC
    items_asc, total = feedback_service.list_feedback(
        db=db_session, sort_by="sentiment_score", order="asc"
    )
    assert total >= 3
    scores_asc = [item.sentiment_score for item in items_asc if item.sentiment_score is not None]
    assert scores_asc == sorted(scores_asc)

    # Sort by sentiment_score DESC
    items_desc, _ = feedback_service.list_feedback(
        db=db_session, sort_by="sentiment_score", order="desc"
    )
    scores_desc = [item.sentiment_score for item in items_desc if item.sentiment_score is not None]
    assert scores_desc == sorted(scores_desc, reverse=True)


def test_timestamp_lifecycle_and_updates(db_session):
    """Verifies that updated_at advances upon feedback update."""
    f = feedback_service.create_feedback(
        db=db_session,
        feedback_in=FeedbackCreate(
            source="Email",
            feedback_text="Initial text for update test",
        ),
    )
    initial_created = f.created_at
    initial_updated = f.updated_at
    assert initial_created is not None
    assert initial_updated is not None

    # Perform update
    updated_f = feedback_service.update_feedback(
        db=db_session,
        feedback_id=f.id,
        feedback_in=FeedbackUpdate(feedback_text="Updated text content"),
    )
    assert updated_f.feedback_text == "Updated text content"
    assert updated_f.updated_at >= initial_updated
