"""Authentication and User Pydantic Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, model_validator
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user attributes."""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Registration request payload."""

    password: str = Field(..., min_length=6, max_length=128)
    role: Optional[UserRole] = UserRole.USER
    name: Optional[str] = None

    @model_validator(mode="after")
    def sync_name(self) -> "UserCreate":
        if self.name and not self.full_name:
            self.full_name = self.name
        elif self.full_name and not self.name:
            self.name = self.full_name
        return self


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

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def name(self) -> str:
        return self.full_name or str(self.email).split("@")[0]

    @computed_field
    @property
    def active(self) -> bool:
        return self.is_active

    @computed_field
    @property
    def createdAt(self) -> str:
        return self.created_at.isoformat()


class Token(BaseModel):
    """JWT Bearer token response."""

    access_token: str
    token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

    @model_validator(mode="after")
    def populate_token(self) -> "Token":
        if not self.token:
            self.token = self.access_token
        return self


class RegisterResponse(BaseModel):
    """Registration response DTO supporting both legacy and frontend contracts."""

    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    token: str
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    """Decoded token claims."""

    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
