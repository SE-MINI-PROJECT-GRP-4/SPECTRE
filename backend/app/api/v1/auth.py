"""Authentication API v1 endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.dependencies.auth import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.auth import RegisterResponse, Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user account with required information and password hashing (REQ-AUTH-01, REQ-AUTH-02, REQ-AUTH-03).",
)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> RegisterResponse:
    service = AuthService(db)
    return service.register(payload)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticates credentials and issues a signed JWT access token (REQ-AUTH-04, REQ-AUTH-05).",
)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    service = AuthService(db)
    return service.login(payload)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Returns the profile information of the currently authenticated bearer token user.",
)
def get_me(current_user: User = Depends(get_current_user)):
    user_dto = UserResponse.model_validate(current_user)
    data = user_dto.model_dump()
    data["user"] = user_dto.model_dump()
    return data


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Performs secure client-side session invalidation acknowledgment (REQ-AUTH-08).",
)
def logout_user(current_user: Optional[User] = Depends(get_optional_user)):
    return {
        "status": "success",
        "message": "Successfully logged out. Please clear authentication tokens from client storage.",
    }
