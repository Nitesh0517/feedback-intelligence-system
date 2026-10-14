from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SentimentDistribution(BaseModel):
    positive: float = Field(default=0.0, description="Percentage of positive feedback")
    neutral: float = Field(default=0.0, description="Percentage of neutral feedback")
    negative: float = Field(default=0.0, description="Percentage of negative feedback")


class AnalyticsOverviewResponse(BaseModel):
    total_feedback: int
    positive_count: int
    negative_count: int
    neutral_count: int
    analyzed_count: int
    pending_count: int
    sentiment_distribution: SentimentDistribution


class SentimentAnalyticsResponse(BaseModel):
    total: int
    positive: int
    negative: int
    neutral: int
    percentages: SentimentDistribution
    average_sentiment_score: Optional[float] = None


class CategoryAnalyticsResponse(BaseModel):
    categories: Dict[str, int]
    total: int
    percentages: Dict[str, float]
    uncategorized: int


class TrendDataPoint(BaseModel):
    date: str
    count: int
    positive_count: int
    negative_count: int
    neutral_count: int


class TrendAnalyticsResponse(BaseModel):
    data_points: List[TrendDataPoint]
    start_date: str
    end_date: str
    total_volume: int
    negative_spike_detected: bool = False
    spike_message: Optional[str] = None
    summary: Optional[str] = None
    recommendations: Optional[List[str]] = None
