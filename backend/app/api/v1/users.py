from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserListResponse,
    UserUpdate,
    UserRoleUpdate,
    UserStatusUpdate,
)
from app.services import user_service
from app.api.deps import require_admin
from app.core.errors import NotFoundException

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List users (Admin only)",
)
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    role: Optional[str] = Query(default=None, description="Filter by user role"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Retrieves paginated list of registered users. Requires administrator role."""
    items, total = user_service.list_users(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
    )
    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user details (Admin only)",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Retrieves detailed profile of a specific user. Requires administrator role."""
    user = user_service.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise NotFoundException(f"User with ID {user_id} not found.")
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user profile (Admin only)",
)
def update_user_profile(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Updates name or email of a user. Requires administrator role."""
    updated = user_service.update_user(db=db, user_id=user_id, user_in=user_in)
    return UserResponse.model_validate(updated)


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Change user role (Admin only)",
)
def change_user_role(
    user_id: int,
    role_in: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Updates the operational role assigned to a user account.
    Guards against demoting the last active administrator.
    """
    updated = user_service.update_user_role(
        db=db,
        user_id=user_id,
        new_role=role_in.role,
        current_admin_id=current_admin.id,
    )
    return UserResponse.model_validate(updated)


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user status (Admin only)",
)
def change_user_status(
    user_id: int,
    status_in: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Activates or deactivates a user account.
    Guards against self-deactivation or deactivation of the last active administrator.
    """
    updated = user_service.update_user_status(
        db=db,
        user_id=user_id,
        is_active=status_in.is_active,
        current_admin_id=current_admin.id,
    )
    return UserResponse.model_validate(updated)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete user (Admin only)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Permanently deletes a user account.
    Guards against self-deletion or deletion of the last active administrator.
    """
    user_service.delete_user(
        db=db,
        user_id=user_id,
        current_admin_id=current_admin.id,
    )
    return {"detail": f"User {user_id} deleted successfully", "id": user_id}
