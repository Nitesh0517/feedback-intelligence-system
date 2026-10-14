from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    SentimentAnalyticsResponse,
    CategoryAnalyticsResponse,
    TrendAnalyticsResponse,
)
from app.services import analytics_service
from app.core.errors import AppBaseException
from app.api.deps import require_authenticated

router = APIRouter(dependencies=[Depends(require_authenticated)])



@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get overview analytics",
)
def get_overview_analytics(db: Session = Depends(get_db)):
    """Returns top-level feedback metrics including total, sentiment counts, and analyzed status."""
    return analytics_service.get_overview(db=db)


@router.get(
    "/sentiment",
    response_model=SentimentAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get sentiment analytics",
)
def get_sentiment_analytics(db: Session = Depends(get_db)):
    """Returns actual sentiment distribution and average score from database."""
    return analytics_service.get_sentiment_analytics(db=db)


@router.get(
    "/categories",
    response_model=CategoryAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category analytics",
)
def get_category_analytics(db: Session = Depends(get_db)):
    """Returns breakdown of customer feedback across operational categories."""
    return analytics_service.get_category_analytics(db=db)


@router.get(
    "/trends",
    response_model=TrendAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get sentiment trends over time",
)
def get_trend_analytics(
    days: int = Query(default=30, ge=1, le=365, description="Lookback window in days"),
    start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """Returns daily time-series volume, sentiment trends, and negative spike detection."""
    today = date.today()

    if start_date and end_date:
        if start_date > end_date:
            raise AppBaseException(
                message="start_date cannot be after end_date.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="INVALID_DATE_RANGE",
            )
        eff_start = start_date
        eff_end = end_date
    elif start_date and not end_date:
        eff_start = start_date
        eff_end = today
        if eff_start > eff_end:
            raise AppBaseException(
                message="start_date cannot be in the future.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="INVALID_DATE_RANGE",
            )
    elif end_date and not start_date:
        eff_end = end_date
        eff_start = eff_end - timedelta(days=days - 1)
    else:
        eff_end = today
        eff_start = eff_end - timedelta(days=days - 1)

    return analytics_service.get_trend_analytics(
        db=db,
        start_date=eff_start,
        end_date=eff_end,
    )
