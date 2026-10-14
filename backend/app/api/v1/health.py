from datetime import datetime, timezone
from fastapi import APIRouter, status, Response
from app.core.config import settings
from app.db.session import check_db_connection, check_redis_connection
from app.schemas.health import HealthResponse, ReadyResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Liveness Probe")
def health_check():
    """Liveness probe to check if the application is running."""
    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc),
        environment=settings.ENVIRONMENT,
    )


@router.get("/ready", response_model=ReadyResponse, summary="Readiness Probe")
def readiness_check(response: Response):
    """Readiness probe to verify database and downstream connectivity."""
    db_ok = check_db_connection()
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        db_status = "unreachable"
    else:
        db_status = "healthy"

    redis_ok = check_redis_connection()
    if redis_ok is None:
        redis_status = "mocked_in_testing" if settings.ENVIRONMENT == "testing" else "not_configured"
    elif redis_ok:
        redis_status = "healthy"
    else:
        redis_status = "unreachable"

    return ReadyResponse(
        status="ready" if db_ok else "not_ready",
        database=db_status,
        redis=redis_status,
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc),
    )
