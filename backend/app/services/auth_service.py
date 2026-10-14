from typing import Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, LoginRequest
from app.core.security import verify_password, create_access_token
from app.core.errors import UnauthorizedException, BadRequestException
from app.services import user_service
from app.core.logging import logger


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Validates user credentials. Prevents revealing whether the email exists
    by returning identical unauthorized error messages for missing accounts or wrong passwords.
    """
    user = user_service.get_user_by_email(db, email)
    if not user:
        logger.warning(f"Failed login attempt for unknown or invalid email.")
        raise UnauthorizedException("Incorrect email or password.")

    if not user.is_active:
        logger.warning(f"Login attempt for deactivated user id={user.id}")
        raise UnauthorizedException("Account is deactivated. Please contact an administrator.")

    if not verify_password(password, user.hashed_password):
        logger.warning(f"Invalid password attempt for user id={user.id}")
        raise UnauthorizedException("Incorrect email or password.")

    return user


def register_user(db: Session, user_in: UserCreate) -> Tuple[User, str]:
    """Registers a new user (with viewer or analyst role) and issues an initial access token."""
    user = user_service.create_user(db, user_in)
    access_token = create_access_token(
        subject=user.id,
        role=user.role,
        name=user.name,
        extra_claims={"email": user.email},
    )
    return user, access_token


def login_user(db: Session, login_in: LoginRequest) -> Tuple[User, str]:
    """Authenticates a user and generates a signed JWT access token."""
    user = authenticate_user(db, login_in.email, login_in.password)
    access_token = create_access_token(
        subject=user.id,
        role=user.role,
        name=user.name,
        extra_claims={"email": user.email},
    )
    return user, access_token
