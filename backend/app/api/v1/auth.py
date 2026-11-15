from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RegisterRequest,
    UserResponse,
)
from app.services.auth.service import (
    authenticate_user,
    register_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new SPECTRE user.
    """

    try:
        user = register_user(
            db=db,
            name=request.name,
            email=request.email,
            password=request.password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return user


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate an existing SPECTRE user.
    """

    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return LoginResponse(
        message="Login successful.",
        user=user,
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
)
def logout():
    """
    Logout endpoint.

    Session/token invalidation will be connected
    when authentication session management is added.
    """

    return LogoutResponse(
        message="Logout successful."
    )