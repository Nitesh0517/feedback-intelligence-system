from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user")
    email: EmailStr = Field(..., description="Unique user email address")


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plaintext password (min 8 chars, including at least one number and letter)",
    )
    role: Optional[str] = Field(
        default="viewer",
        description="User operational role (viewer, analyst). Admin role cannot be created via public registration.",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one numeric digit.")
        return v

    @field_validator("role")
    @classmethod
    def validate_public_registration_role(cls, v: Optional[str]) -> str:
        if v is None:
            return "viewer"
        role_normalized = v.strip().lower()
        if role_normalized == "admin":
            raise ValueError("Administrator accounts cannot be created via public registration.")
        if role_normalized not in ["analyst", "viewer"]:
            raise ValueError(f"Invalid role '{v}'. Allowed roles are 'analyst' and 'viewer'.")
        return role_normalized


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None


class UserRoleUpdate(BaseModel):
    role: str = Field(..., description="Target role: admin, analyst, or viewer")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        role_normalized = v.strip().lower()
        if role_normalized not in ["admin", "analyst", "viewer"]:
            raise ValueError(f"Invalid role '{v}'. Must be one of: 'admin', 'analyst', 'viewer'.")
        return role_normalized


class UserStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Account active status")


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    skip: int
    limit: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
