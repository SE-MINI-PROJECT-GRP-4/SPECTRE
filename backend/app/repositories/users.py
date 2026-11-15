"""User repository for database operations."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User, UserRole


class UserRepository:
    """Repository handling CRUD operations for User entities."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.scalar(select(User).where(User.id == user_id))

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.scalar(select(User).where(User.email == email.lower().strip()))

    def create(self, email: str, hashed_password: str, full_name: Optional[str] = None, role: UserRole = UserRole.USER) -> User:
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(self, skip: int = 0, limit: int = 50) -> List[User]:
        return list(self.db.scalars(select(User).offset(skip).limit(limit)).all())

    def update_role(self, user: User, role: UserRole) -> User:
        user.role = role
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_status(self, user: User, is_active: bool) -> User:
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user
