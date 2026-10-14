from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class FeedbackBase(BaseModel):
    source: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Origin channel of feedback (e.g. Web Form, Email, Mobile App, Survey)",
    )
    customer_identifier: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional customer ID, username, or email identifier",
    )
    feedback_text: str = Field(
        ...,
        min_length=3,
        max_length=10000,
        description="Raw textual content of customer feedback",
    )

    @field_validator("source", "feedback_text")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            val = v.strip()
            if not val:
                raise ValueError("Field cannot be empty or purely whitespace.")
            return val
        return v

    @field_validator("customer_identifier")
    @classmethod
    def clean_customer_identifier(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            cleaned = v.strip()
            return cleaned if cleaned else None
        return None


class FeedbackCreate(FeedbackBase):
    category: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Operational category (e.g. Product Quality, Customer Support)",
    )
    sentiment: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Sentiment classification: positive, negative, or neutral",
    )
    sentiment_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence or intensity score between 0.0 and 1.0",
    )


class FeedbackUpdate(BaseModel):
    source: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    customer_identifier: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    feedback_text: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=10000,
    )
    category: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    sentiment: Optional[str] = Field(
        default=None,
        max_length=50,
    )
    sentiment_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    status: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    @field_validator("feedback_text", "source")
    @classmethod
    def strip_if_present(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            val = v.strip()
            if not val:
                raise ValueError("Field cannot be empty or whitespace.")
            return val
        return v


class FeedbackResponse(FeedbackBase):
    id: int
    category: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackListResponse(BaseModel):
    items: List[FeedbackResponse]
    total: int
    skip: int
    limit: int
