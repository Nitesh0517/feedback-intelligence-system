from typing import Tuple
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, LoginRequest
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.errors import UnauthorizedException, BadRequestException
from app.services import user_service
from app.core.logging import logger
from app.core.config import settings


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Validates user credentials.
    In development mode, auto-provisions or accepts any email and password
    so the user can immediately log in with any credentials.
    In testing/production mode, strictly enforces credential verification.
    """
    normalized_email = email.strip().lower()
    user = user_service.get_user_by_email(db, normalized_email)

    # Development auto-login mode: accept ANY email and password
    if settings.ENVIRONMENT != "testing" and settings.ENVIRONMENT != "production":
        if not user:
            name_part = normalized_email.split("@")[0].replace(".", " ").capitalize()
            user = User(
                name=name_part if name_part else "Demo User",
                email=normalized_email,
                hashed_password=get_password_hash(password),
                role=UserRole.ADMIN.value,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Dev mode auto-created admin user: {normalized_email}")
            return user
        else:
            if not user.is_active:
                user.is_active = True
            if not verify_password(password, user.hashed_password):
                user.hashed_password = get_password_hash(password)
            db.commit()
            db.refresh(user)
            return user

    # Strict production and test authentication
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
