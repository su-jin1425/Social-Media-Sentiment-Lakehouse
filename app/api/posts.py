import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.social_post import SocialPostResponse, SocialPostListResponse
from app.services.post_service import PostService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/posts", tags=["Social Posts"])


@router.get("", response_model=SocialPostListResponse)
def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    platform: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SocialPostListResponse:
    """Return a paginated list of social media posts."""
    service = PostService(db)
    return service.list_posts(page=page, page_size=page_size, platform=platform)


@router.get("/trending", response_model=list[SocialPostResponse])
def get_trending(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SocialPostResponse]:
    """Return trending social media posts."""
    service = PostService(db)
    return service.get_trending(limit=limit)


@router.get("/{post_id}", response_model=SocialPostResponse)
def get_post(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SocialPostResponse:
    """Return a single social media post by its ID."""
    service = PostService(db)
    return service.get_post(post_id)
