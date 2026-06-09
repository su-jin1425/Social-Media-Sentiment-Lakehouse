import uuid
import logging
from typing import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_token
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


def get_current_user_id(authorization: str = Header(...)) -> uuid.UUID:
    """Extract and validate the user ID from the Authorization header."""
    if not authorization.startswith("Bearer "):
        raise AuthenticationError(detail="Invalid authorization header format")
    token = authorization[7:]
    try:
        payload = decode_token(token)
    except Exception:
        raise AuthenticationError(detail="Invalid or expired token")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError(detail="Invalid token payload")
    return uuid.UUID(user_id_str)


def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current authenticated user from the database."""
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise AuthenticationError(detail="User not found")
    return user


def require_role(*roles: str):
    """Return a dependency that enforces role-based access control."""
    def _check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise AuthorizationError(
                detail=f"Role '{current_user.role}' is not authorized for this operation"
            )
        return current_user
    return _check_role
