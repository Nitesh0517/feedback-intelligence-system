from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, LoginRequest, TokenResponse, UserResponse
from app.services import auth_service
from app.api.deps import get_current_active_user
from app.core.rate_limit import RateLimiter
from app.core.config import settings
from app.core.security import revoke_token

router = APIRouter()
auth_rate_limiter = RateLimiter(limit=settings.AUTH_RATE_LIMIT_PER_MINUTE, window=60, scope="auth")


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    dependencies=[Depends(auth_rate_limiter)],
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Registers a new user account with role 'viewer' or 'analyst'.
    Administrator privileges cannot be created via public registration.
    """
    user, access_token = auth_service.register_user(db=db, user_in=user_in)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    dependencies=[Depends(auth_rate_limiter)],
)
def login(
    login_in: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticates user with email and password and returns a signed JWT access token.
    Protected by rate limiting against brute-force attacks.
    """
    user, access_token = auth_service.login_user(db=db, login_in=login_in)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """Returns profile details and assigned role for the authenticated user."""
    return UserResponse.model_validate(current_user)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
)
def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """
    Logs out the authenticated user.
    Stateless JWT tokens are invalidated both server-side and on client storage.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        revoke_token(token)

    return {
        "detail": "Successfully logged out. Please discard client-stored tokens.",
        "user_id": current_user.id,
    }
