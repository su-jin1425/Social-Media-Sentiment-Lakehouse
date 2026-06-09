from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import (
    AuthenticationError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, TokenResponse


class AuthService:
    """Service layer handling user authentication and registration."""

    def __init__(self, db: Session) -> None:
        self._repo = UserRepository(db)

    def register(self, data: UserCreate) -> UserResponse:
        """Register a new user. Raises DuplicateEntityError if email is taken."""
        existing = self._repo.get_by_email(data.email)
        if existing:
            raise DuplicateEntityError("User", "email", data.email)

        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=UserRole.VIEWER,
        )
        created = self._repo.create(user)
        return UserResponse.model_validate(created)

    def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate a user and return JWT tokens."""
        user = self._repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def get_current_user(self, user_id: int) -> UserResponse:
        """Retrieve the currently authenticated user profile."""
        user = self._repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        return UserResponse.model_validate(user)
