"""Authentication service orchestrating registration and login."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.users import UserRepository
from app.schemas.auth import RegisterResponse, Token, UserCreate, UserLogin, UserResponse


class AuthService:
    """Service handling credential verification, user registration, and JWT token issuance."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def register(self, data: UserCreate) -> RegisterResponse:
        """Register a new user account (REQ-AUTH-01, REQ-AUTH-02, REQ-AUTH-03)."""
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        hashed = hash_password(data.password)
        role = data.role or UserRole.USER
        user = self.repo.create(
            email=data.email,
            hashed_password=hashed,
            full_name=data.full_name,
            role=role,
        )
        token = create_access_token(subject=user.id, role=user.role.value)
        user_dto = UserResponse.model_validate(user)
        return RegisterResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            token=token,
            access_token=token,
            token_type="bearer",
            user=user_dto,
        )

    def login(self, data: UserLogin) -> Token:
        """Authenticate user credentials and issue signed JWT token (REQ-AUTH-04, REQ-AUTH-05)."""
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated. Please contact support.",
            )

        access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )
