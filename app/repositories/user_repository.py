import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Data access layer for User entities."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Retrieve a user by primary key."""
        return self._db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email address."""
        return self._db.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        """Persist a new user to the database."""
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Return a paginated list of users."""
        return self._db.query(User).offset(skip).limit(limit).all()
