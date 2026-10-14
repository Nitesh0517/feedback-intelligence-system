from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    CheckConstraint,
    Index,
)
from app.db.session import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.VIEWER.value, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'analyst', 'viewer')",
            name="ck_user_role_valid",
        ),
        Index("ix_users_email_active", "email", "is_active"),
    )

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' role='{self.role}' active={self.is_active}>"
