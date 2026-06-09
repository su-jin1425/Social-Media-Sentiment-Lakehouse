from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError
from app.models.social_post import SocialPost
from app.repositories.post_repository import PostRepository
from app.schemas.social_post import SocialPostCreate, SocialPostResponse


class PostService:
    """Service layer for social post operations."""

    def __init__(self, db: Session) -> None:
        self._repo = PostRepository(db)

    def list_posts(
        self, skip: int = 0, limit: int = 50
    ) -> list[SocialPostResponse]:
        """Return a paginated list of social posts."""
        posts = self._repo.list_all(skip=skip, limit=limit)
        return [SocialPostResponse.model_validate(p) for p in posts]

    def get_post(self, post_id: int) -> SocialPostResponse:
        """Retrieve a single post by id."""
        post = self._repo.get_by_id(post_id)
        if not post:
            raise EntityNotFoundError("SocialPost", post_id)
        return SocialPostResponse.model_validate(post)

    def get_trending(self, limit: int = 20) -> list[SocialPostResponse]:
        """Return trending posts ranked by engagement."""
        posts = self._repo.get_trending(limit=limit)
        return [SocialPostResponse.model_validate(p) for p in posts]

    def create_post(self, data: SocialPostCreate) -> SocialPostResponse:
        """Create and persist a new social post."""
        post = SocialPost(
            platform=data.platform,
            author_name=data.author_name,
            content=data.content,
            source_id=data.source_id,
        )
        created = self._repo.create(post)
        return SocialPostResponse.model_validate(created)
