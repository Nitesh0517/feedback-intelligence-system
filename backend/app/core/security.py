from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import bcrypt
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.core.config import settings
from app.core.errors import UnauthorizedException
from app.core.logging import logger


def get_password_hash(password: str) -> str:
    """Hashes a plaintext password using bcrypt with a random salt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Safely verifies a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception as exc:
        logger.warning(f"Password verification error: {exc}")
        return False


def create_access_token(
    subject: Union[str, int],
    role: str,
    name: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Creates a signed, expiration-bounded JSON Web Token (JWT).
    Subject contains user identifier (email or user ID).
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "name": name or "",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# In-memory revocation cache for development/testing; synced to Redis when configured
_revoked_tokens: set = set()


def revoke_token(token: str) -> None:
    """Revokes an active access token."""
    _revoked_tokens.add(token)
    if settings.REDIS_URL and settings.ENVIRONMENT != "testing":
        try:
            import redis
            client = redis.Redis.from_url(settings.REDIS_URL)
            client.setex(f"denylist:{token}", int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()), "1")
        except Exception as e:
            logger.warning(f"Could not persist revoked token to Redis: {e}")


def is_token_revoked(token: str) -> bool:
    """Checks whether an access token has been revoked."""
    if token in _revoked_tokens:
        return True
    if settings.REDIS_URL and settings.ENVIRONMENT != "testing":
        try:
            import redis
            client = redis.Redis.from_url(settings.REDIS_URL)
            return bool(client.exists(f"denylist:{token}"))
        except Exception:
            pass
    return False


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates JWT signature, issuer, expiration, and revocation status.
    Raises UnauthorizedException on invalid, expired, or revoked token.
    """
    if is_token_revoked(token):
        logger.debug("Attempt to authenticate with a revoked token.")
        raise UnauthorizedException("Authentication token has been revoked. Please log in again.")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        logger.debug("Access token signature has expired.")
        raise UnauthorizedException("Authentication token has expired. Please log in again.")
    except InvalidTokenError as exc:
        logger.warning(f"Invalid access token format or signature: {str(exc)}")
        raise UnauthorizedException("Invalid authentication credentials.")
