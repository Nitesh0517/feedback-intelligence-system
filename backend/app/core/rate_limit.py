import time
from typing import Dict, List, Tuple
from collections import defaultdict
from fastapi import Request, status, HTTPException

from app.core.config import settings
from app.core.logging import logger

# In-memory sliding-window store: key -> list of timestamps
_request_history: Dict[str, List[float]] = defaultdict(list)


def is_rate_limit_exceeded(key: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
    """
    Checks if a key (e.g. client IP + route scope) has exceeded the permitted limit
    within the sliding window. Returns (is_exceeded, remaining_calls, retry_after_seconds).
    """
    now = time.time()
    cutoff = now - window_seconds
    timestamps = _request_history[key]

    # Purge timestamps outside current window
    _request_history[key] = [t for t in timestamps if t > cutoff]
    active_count = len(_request_history[key])

    if active_count >= limit:
        oldest = _request_history[key][0]
        retry_after = max(1, int(oldest + window_seconds - now))
        return True, 0, retry_after

    _request_history[key].append(now)
    remaining = max(0, limit - (active_count + 1))
    return False, remaining, 0


def clear_rate_limits():
    """Clears rate limit state (useful in test suites)."""
    _request_history.clear()


class RateLimiter:
    """FastAPI dependency for endpoint-level rate limiting."""

    def __init__(self, limit: int = 60, window: int = 60, scope: str = "general"):
        self.limit = limit
        self.window = window
        self.scope = scope

    async def __call__(self, request: Request):
        if not settings.RATE_LIMIT_ENABLED or settings.ENVIRONMENT == "testing":
            return

        client_ip = request.client.host if request.client else "unknown"
        key = f"{self.scope}:{client_ip}"

        exceeded, remaining, retry_after = is_rate_limit_exceeded(
            key, self.limit, self.window
        )

        if exceeded:
            logger.warning(f"Rate limit exceeded for {key} ({self.limit} req/{self.window}s)")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please retry after {retry_after} seconds.",
                headers={"Retry-After": str(retry_after), "X-RateLimit-Limit": str(self.limit)},
            )
