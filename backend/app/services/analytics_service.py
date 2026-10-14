from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.feedback import Feedback
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    SentimentAnalyticsResponse,
    CategoryAnalyticsResponse,
    TrendAnalyticsResponse,
    TrendDataPoint,
    SentimentDistribution,
)
from app.core.logging import logger

STANDARD_CATEGORIES = [
    "Product Quality",
    "Customer Support",
    "Pricing",
    "Delivery",
    "User Experience",
    "Feature Request",
    "Other",
]


def get_overview(db: Session) -> AnalyticsOverviewResponse:
    """Aggregates high-level metrics across the entire feedback repository."""
    stats = db.query(
        func.count(Feedback.id).label("total"),
        func.sum(case((Feedback.sentiment == "positive", 1), else_=0)).label("positive"),
        func.sum(case((Feedback.sentiment == "negative", 1), else_=0)).label("negative"),
        func.sum(case((Feedback.sentiment == "neutral", 1), else_=0)).label("neutral"),
        func.sum(case((Feedback.status == "analyzed", 1), else_=0)).label("analyzed"),
    ).first()

    total = int(stats.total or 0)
    positive = int(stats.positive or 0)
    negative = int(stats.negative or 0)
    neutral = int(stats.neutral or 0)
    analyzed = int(stats.analyzed or 0)
    pending = max(0, total - analyzed)

    if total > 0:
        pos_pct = round((positive / total) * 100, 1)
        neg_pct = round((negative / total) * 100, 1)
        neu_pct = round((neutral / total) * 100, 1)
    else:
        pos_pct = neg_pct = neu_pct = 0.0

    return AnalyticsOverviewResponse(
        total_feedback=total,
        positive_count=positive,
        negative_count=negative,
        neutral_count=neutral,
        analyzed_count=analyzed,
        pending_count=pending,
        sentiment_distribution=SentimentDistribution(
            positive=pos_pct,
            neutral=neu_pct,
            negative=neg_pct,
        ),
    )


def get_sentiment_analytics(db: Session) -> SentimentAnalyticsResponse:
    """Calculates detailed sentiment counts, percentages, and average score."""
    stats = db.query(
        func.count(Feedback.id).label("total"),
        func.sum(case((Feedback.sentiment == "positive", 1), else_=0)).label("positive"),
        func.sum(case((Feedback.sentiment == "negative", 1), else_=0)).label("negative"),
        func.sum(case((Feedback.sentiment == "neutral", 1), else_=0)).label("neutral"),
        func.avg(Feedback.sentiment_score).label("avg_score"),
    ).first()

    total = int(stats.total or 0)
    positive = int(stats.positive or 0)
    negative = int(stats.negative or 0)
    neutral = int(stats.neutral or 0)
    avg_score = float(stats.avg_score) if stats.avg_score is not None else None

    if total > 0:
        pos_pct = round((positive / total) * 100, 1)
        neg_pct = round((negative / total) * 100, 1)
        neu_pct = round((neutral / total) * 100, 1)
    else:
        pos_pct = neg_pct = neu_pct = 0.0

    return SentimentAnalyticsResponse(
        total=total,
        positive=positive,
        negative=negative,
        neutral=neutral,
        percentages=SentimentDistribution(
            positive=pos_pct,
            neutral=neu_pct,
            negative=neg_pct,
        ),
        average_sentiment_score=round(avg_score, 4) if avg_score is not None else None,
    )


def get_category_analytics(db: Session) -> CategoryAnalyticsResponse:
    """Returns feedback counts and percentages grouped by operational category."""
    raw_counts = (
        db.query(Feedback.category, func.count(Feedback.id))
        .group_by(Feedback.category)
        .all()
    )

    categories_dict: Dict[str, int] = {cat: 0 for cat in STANDARD_CATEGORIES}
    uncategorized = 0
    total = 0

    for cat_name, count in raw_counts:
        count_int = int(count)
        total += count_int
        if not cat_name:
            uncategorized += count_int
            categories_dict["Other"] += count_int
        elif cat_name in categories_dict:
            categories_dict[cat_name] += count_int
        else:
            categories_dict["Other"] += count_int

    percentages: Dict[str, float] = {}
    for cat, c_count in categories_dict.items():
        percentages[cat] = round((c_count / total * 100), 1) if total > 0 else 0.0

    return CategoryAnalyticsResponse(
        categories=categories_dict,
        total=total,
        percentages=percentages,
        uncategorized=uncategorized,
    )


def get_trend_analytics(
    db: Session,
    start_date: date,
    end_date: date,
) -> TrendAnalyticsResponse:
    """
    Computes time-series data points grouped by day within the given date range.
    Fills in zero-volume dates to maintain continuous trend line graphs.
    Detects statistically significant negative feedback spikes.
    """
    # Start and end datetimes
    start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)

    # Aggregated query by date
    results = (
        db.query(
            func.date(Feedback.created_at).label("day"),
            func.count(Feedback.id).label("total_count"),
            func.sum(case((Feedback.sentiment == "positive", 1), else_=0)).label("pos_count"),
            func.sum(case((Feedback.sentiment == "negative", 1), else_=0)).label("neg_count"),
            func.sum(case((Feedback.sentiment == "neutral", 1), else_=0)).label("neu_count"),
        )
        .filter(Feedback.created_at >= start_dt, Feedback.created_at <= end_dt)
        .group_by(func.date(Feedback.created_at))
        .all()
    )

    # Index results by day string (YYYY-MM-DD)
    day_map: Dict[str, Dict[str, int]] = {}
    for r in results:
        day_str = str(r.day)
        day_map[day_str] = {
            "count": int(r.total_count or 0),
            "positive_count": int(r.pos_count or 0),
            "negative_count": int(r.neg_count or 0),
            "neutral_count": int(r.neu_count or 0),
        }

    # Generate continuous daily series
    current = start_date
    data_points: List[TrendDataPoint] = []
    total_volume = 0
    total_negative = 0

    while current <= end_date:
        d_str = current.isoformat()
        metrics = day_map.get(
            d_str,
            {"count": 0, "positive_count": 0, "negative_count": 0, "neutral_count": 0},
        )
        data_points.append(
            TrendDataPoint(
                date=d_str,
                count=metrics["count"],
                positive_count=metrics["positive_count"],
                negative_count=metrics["negative_count"],
                neutral_count=metrics["neutral_count"],
            )
        )
        total_volume += metrics["count"]
        total_negative += metrics["negative_count"]
        current += timedelta(days=1)

    # Spike Detection: evaluate recent 3 days vs historical average
    spike_detected = False
    spike_message = None

    if len(data_points) >= 6 and total_volume >= 5:
        recent_pts = data_points[-3:]
        older_pts = data_points[:-3]

        recent_total = sum(p.count for p in recent_pts)
        recent_neg = sum(p.negative_count for p in recent_pts)

        older_total = sum(p.count for p in older_pts)
        older_neg = sum(p.negative_count for p in older_pts)

        if older_total > 0 and recent_total > 0:
            hist_neg_rate = older_neg / older_total
            recent_neg_rate = recent_neg / recent_total

            # If recent negative rate exceeds historical rate by > 1.5x and has >= 2 negative feedbacks
            if recent_neg >= 2 and recent_neg_rate > (hist_neg_rate * 1.5 + 0.15):
                spike_detected = True
                pct_increase = round((recent_neg_rate - hist_neg_rate) * 100, 1)
                spike_message = (
                    f"Noticeable spike in negative customer sentiment detected over the last 3 days "
                    f"(+{pct_increase}% above baseline rate)."
                )

    # Generate grounded summary and recommendations
    if total_volume == 0:
        summary = "No feedback records were submitted within the specified time range."
        recommendations = [
            "Encourage users to submit reviews across active touchpoints.",
            "Integrate automatic feedback prompts into key customer workflows.",
        ]
    else:
        neg_rate = round((total_negative / total_volume) * 100, 1)
        summary = (
            f"Over the period from {start_date} to {end_date}, a total of {total_volume} feedback items "
            f"were ingested. Negative feedback accounts for {neg_rate}% of the total volume."
        )
        recommendations = [
            "Prioritize top negative feedback items in Customer Support and Delivery.",
            "Monitor trending issues to prevent further escalations.",
            "Follow up directly with customers who left low-scoring sentiment feedback.",
        ]

    return TrendAnalyticsResponse(
        data_points=data_points,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        total_volume=total_volume,
        negative_spike_detected=spike_detected,
        spike_message=spike_message,
        summary=summary,
        recommendations=recommendations,
    )
