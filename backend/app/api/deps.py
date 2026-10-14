from typing import Optional, Callable
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.security import decode_access_token
from app.core.errors import UnauthorizedException, ForbiddenException
from app.services import user_service

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extracts and validates JWT Bearer token from Authorization header.
    Retrieves the authenticated active user from the database.
    """
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authentication credentials were not provided.")

    token = credentials.credentials
    payload = decode_access_token(token)

    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedException("Invalid authentication token payload.")

    try:
        user_id = int(sub)
        user = user_service.get_user_by_id(db, user_id=user_id)
    except (ValueError, TypeError):
        user = user_service.get_user_by_email(db, email=str(sub))

    if not user:
        raise UnauthorizedException("User account associated with this token was not found.")

    if not user.is_active:
        raise UnauthorizedException("User account is deactivated. Please contact an administrator.")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensures the authenticated user account is active."""
    if not current_user.is_active:
        raise UnauthorizedException("User account is inactive.")
    return current_user


def require_roles(*allowed_roles: str) -> Callable[[User], User]:
    """
    Role-Based Access Control dependency factory.
    Verifies that the authenticated user possesses at least one of the permitted roles.
    Raises HTTP 403 Forbidden on authorization failure.
    """
    normalized_roles = [r.lower() for r in allowed_roles]

    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role.lower() not in normalized_roles:
            raise ForbiddenException(
                f"Access denied. Requires one of roles: {', '.join(allowed_roles)}. "
                f"Your current role is '{current_user.role}'."
            )
        return current_user

    return role_checker


# Role shortcut dependencies
require_admin = require_roles(UserRole.ADMIN.value)
require_analyst_or_admin = require_roles(UserRole.ADMIN.value, UserRole.ANALYST.value)
require_authenticated = get_current_active_user
