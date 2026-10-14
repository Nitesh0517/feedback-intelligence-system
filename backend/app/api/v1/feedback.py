from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackResponse,
    FeedbackListResponse,
)
from app.services import feedback_service, feedback_analysis_service
from app.tasks.feedback_tasks import analyze_feedback_task, batch_analyze_feedback_task
from app.schemas.tasks import TaskEnqueueResponse
from app.core.errors import NotFoundException
from app.api.deps import require_authenticated, require_analyst_or_admin, require_admin

router = APIRouter()


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create feedback",
)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """Creates a new customer feedback entry. Requires Analyst or Admin role."""
    return feedback_service.create_feedback(db=db, feedback_in=feedback_in)


@router.get(
    "",
    response_model=FeedbackListResponse,
    status_code=status.HTTP_200_OK,
    summary="List feedback",
)
def list_feedback(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
    search: Optional[str] = Query(default=None, description="Search term in text or customer ID"),
    category: Optional[str] = Query(default=None, description="Filter by operational category"),
    sentiment: Optional[str] = Query(default=None, description="Filter by sentiment"),
    source: Optional[str] = Query(default=None, description="Filter by channel source"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by (created_at, sentiment_score, id, updated_at)"),
    order: Optional[str] = Query(default="desc", description="Sort direction: asc or desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """Returns a paginated list of feedback records. Accessible to Viewer, Analyst, and Admin."""
    items, total = feedback_service.list_feedback(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        sentiment=sentiment,
        source=source,
        status=status,
        sort_by=sort_by or "created_at",
        order=order or "desc",
    )
    return FeedbackListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Get feedback by ID",
)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """Retrieves a single feedback record by ID. Accessible to Viewer, Analyst, and Admin."""
    item = feedback_service.get_feedback_by_id(db=db, feedback_id=feedback_id)
    if not item:
        raise NotFoundException(f"Feedback with id {feedback_id} not found")
    return item


@router.patch(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Update feedback",
)
def update_feedback(
    feedback_id: int,
    feedback_in: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """Updates fields of an existing feedback record. Requires Analyst or Admin role."""
    updated = feedback_service.update_feedback(
        db=db,
        feedback_id=feedback_id,
        feedback_in=feedback_in,
    )
    if not updated:
        raise NotFoundException(f"Feedback with id {feedback_id} not found")
    return updated


@router.delete(
    "/{feedback_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete feedback",
)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deletes a feedback record by ID. Strictly requires Admin role."""
    deleted = feedback_service.delete_feedback(db=db, feedback_id=feedback_id)
    if not deleted:
        raise NotFoundException(f"Feedback with id {feedback_id} not found")
    return {"detail": "Feedback deleted successfully", "id": feedback_id}


@router.post(
    "/batch-analyze",
    status_code=status.HTTP_200_OK,
    summary="Batch analyze feedback",
)
def batch_analyze_feedback(
    limit: int = Query(default=50, ge=1, le=200, description="Max items to process"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """Processes unanalyzed customer feedback items in bulk synchronously. Requires Analyst or Admin role."""
    return feedback_analysis_service.batch_analyze_pending(db=db, limit=limit)


@router.post(
    "/batch-analyze-async",
    response_model=TaskEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Batch analyze feedback asynchronously",
)
@router.post(
    "/analyze-batch-async",
    response_model=TaskEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
    include_in_schema=False,
)
def batch_analyze_feedback_async(
    limit: int = Query(default=50, ge=1, le=200, description="Max items to process"),
    current_user: User = Depends(require_analyst_or_admin),
):
    """Enqueues a background Celery task to batch process pending feedback. Requires Analyst or Admin role."""
    task = batch_analyze_feedback_task.delay(limit=limit)
    return TaskEnqueueResponse(
        task_id=task.id,
        status="PENDING",
        message=f"Batch analysis task enqueued successfully for up to {limit} items",
    )


@router.post(
    "/{feedback_id}/analyze",
    response_model=FeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze feedback",
)
def analyze_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """Triggers complete AI/ML sentiment analysis and categorization pipeline synchronously. Requires Analyst or Admin role."""
    return feedback_analysis_service.analyze_and_update_feedback(db=db, feedback_id=feedback_id)


@router.post(
    "/{feedback_id}/analyze-async",
    response_model=TaskEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Analyze feedback asynchronously",
)
def analyze_feedback_async(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """Enqueues background Celery task for feedback sentiment and category analysis. Requires Analyst or Admin role."""
    feedback = feedback_service.get_feedback_by_id(db=db, feedback_id=feedback_id)
    if not feedback:
        raise NotFoundException(f"Feedback with id {feedback_id} not found")

    task = analyze_feedback_task.delay(feedback_id=feedback_id)
    return TaskEnqueueResponse(
        task_id=task.id,
        status="PENDING",
        message=f"Analysis task for feedback {feedback_id} enqueued successfully",
    )
