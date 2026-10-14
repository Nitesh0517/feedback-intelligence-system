from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    CheckConstraint,
    Index,
)
from app.db.session import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source = Column(String(100), nullable=False, index=True)
    customer_identifier = Column(String(255), nullable=True, index=True)
    feedback_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    sentiment = Column(String(50), nullable=True, index=True)
    sentiment_score = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, default="new", index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "sentiment_score IS NULL OR (sentiment_score >= 0.0 AND sentiment_score <= 1.0)",
            name="ck_feedback_sentiment_score_range",
        ),
        Index("ix_feedbacks_created_sentiment", "created_at", "sentiment"),
        Index("ix_feedbacks_category_sentiment", "category", "sentiment"),
    )

    def __repr__(self):
        return f"<Feedback id={self.id} source='{self.source}' sentiment='{self.sentiment}' category='{self.category}'>"
