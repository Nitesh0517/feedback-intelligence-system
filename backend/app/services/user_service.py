from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.errors import ConflictException, NotFoundException, BadRequestException
from app.core.config import settings
from app.core.logging import logger


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Retrieves a user by unique primary key ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieves a user by normalized lowercase email address."""
    return db.query(User).filter(func.lower(User.email) == email.strip().lower()).first()


def list_users(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Tuple[List[User], int]:
    """Retrieves a paginated list of users with optional filtering."""
    query = db.query(User)

    if role:
        query = query.filter(User.role == role.strip().lower())
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    items = query.order_by(User.id.asc()).offset(skip).limit(limit).all()
    return items, total


def create_user(
    db: Session,
    user_in: UserCreate,
    role_override: Optional[str] = None,
) -> User:
    """Creates a new user record with securely hashed password."""
    normalized_email = user_in.email.strip().lower()
    existing = get_user_by_email(db, normalized_email)
    if existing:
        raise ConflictException("A user with this email address already exists.")

    assigned_role = role_override if role_override else (user_in.role or UserRole.VIEWER.value)
    hashed_pwd = get_password_hash(user_in.password)

    user = User(
        name=user_in.name.strip(),
        email=normalized_email,
        hashed_password=hashed_pwd,
        role=assigned_role.lower(),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"User created: id={user.id}, email={user.email}, role={user.role}")
    return user


def update_user(db: Session, user_id: int, user_in: UserUpdate) -> User:
    """Updates non-sensitive profile fields of a user."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(f"User with ID {user_id} not found.")

    if user_in.name is not None:
        user.name = user_in.name.strip()
    if user_in.email is not None:
        new_email = user_in.email.strip().lower()
        if new_email != user.email:
            existing = get_user_by_email(db, new_email)
            if existing and existing.id != user_id:
                raise ConflictException("A user with this email address already exists.")
            user.email = new_email

    db.commit()
    db.refresh(user)
    return user


def count_active_admins(db: Session) -> int:
    """Counts the number of active administrators in the system."""
    return db.query(User).filter(
        User.role == UserRole.ADMIN.value,
        User.is_active == True
    ).count()


def update_user_role(db: Session, user_id: int, new_role: str, current_admin_id: int) -> User:
    """Updates a user's role, guarding against removal of the last administrator."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(f"User with ID {user_id} not found.")

    target_role = new_role.strip().lower()
    if target_role not in [r.value for r in UserRole]:
        raise BadRequestException(f"Invalid role: {new_role}")

    # Prevent demoting the last active administrator
    if user.role == UserRole.ADMIN.value and target_role != UserRole.ADMIN.value:
        if count_active_admins(db) <= 1:
            raise BadRequestException("Cannot demote the last remaining active administrator.")

    user.role = target_role
    db.commit()
    db.refresh(user)
    logger.info(f"User {user_id} role updated to '{target_role}' by admin {current_admin_id}")
    return user


def update_user_status(db: Session, user_id: int, is_active: bool, current_admin_id: int) -> User:
    """Activates or deactivates a user account with safety checks."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(f"User with ID {user_id} not found.")

    if not is_active:
        if user_id == current_admin_id:
            raise BadRequestException("Administrators cannot deactivate their own account.")
        if user.role == UserRole.ADMIN.value and count_active_admins(db) <= 1:
            raise BadRequestException("Cannot deactivate the last remaining active administrator.")

    user.is_active = is_active
    db.commit()
    db.refresh(user)
    logger.info(f"User {user_id} active status changed to {is_active} by admin {current_admin_id}")
    return user


def delete_user(db: Session, user_id: int, current_admin_id: int) -> bool:
    """Deletes a user record, preventing self-deletion or deletion of the last admin."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(f"User with ID {user_id} not found.")

    if user_id == current_admin_id:
        raise BadRequestException("Administrators cannot delete their own account.")

    if user.role == UserRole.ADMIN.value and count_active_admins(db) <= 1:
        raise BadRequestException("Cannot delete the last remaining active administrator.")

    db.delete(user)
    db.commit()
    logger.info(f"User {user_id} deleted by admin {current_admin_id}")
    return True


def seed_initial_admin(db: Session) -> Optional[User]:
    """
    Seeds an initial administrator account if configured in environment variables
    and no admin account currently exists.
    """
    if not settings.INITIAL_ADMIN_EMAIL or not settings.INITIAL_ADMIN_PASSWORD:
        return None

    admin_email = settings.INITIAL_ADMIN_EMAIL.strip().lower()
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
    if existing_admin:
        return existing_admin

    existing_user = get_user_by_email(db, admin_email)
    if existing_user:
        existing_user.role = UserRole.ADMIN.value
        existing_user.is_active = True
        db.commit()
        db.refresh(existing_user)
        return existing_user

    admin_user = User(
        name="Initial Administrator",
        email=admin_email,
        hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    logger.info(f"Successfully seeded initial administrator: {admin_email}")
    return admin_user
