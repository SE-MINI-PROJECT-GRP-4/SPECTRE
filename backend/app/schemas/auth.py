"""Authentication and User Pydantic Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user attributes."""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Registration request payload."""

    password: str = Field(..., min_length=6, max_length=128)
    role: Optional[UserRole] = UserRole.USER


class UserLogin(BaseModel):
    """Login request payload."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(UserBase):
    """User profile response DTO."""

    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Bearer token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenPayload(BaseModel):
    """Decoded token claims."""

    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
