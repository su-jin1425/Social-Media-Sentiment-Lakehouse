import uuid
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.social_post import SocialPost


class PostRepository:
    """Data access layer for SocialPost entities."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, post_id: uuid.UUID) -> Optional[SocialPost]:
        """Retrieve a post by primary key."""
        return self._db.query(SocialPost).filter(SocialPost.id == post_id).first()

    def create(self, post: SocialPost) -> SocialPost:
        """Persist a new social post."""
        self._db.add(post)
        self._db.commit()
        self._db.refresh(post)
        return post

    def create_batch(self, posts: list[SocialPost]) -> list[SocialPost]:
        """Persist a batch of social posts."""
        self._db.add_all(posts)
        self._db.commit()
        return posts

    def list_posts(
        self,
        skip: int = 0,
        limit: int = 50,
        platform: Optional[str] = None,
    ) -> tuple[list[SocialPost], int]:
        """Return paginated posts with optional platform filter and total count."""
        query = self._db.query(SocialPost)
        if platform:
            query = query.filter(SocialPost.platform == platform)
        total: int = query.count()
        items = query.order_by(SocialPost.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_trending(
        self, limit: int = 20
    ) -> list[SocialPost]:
        """Return posts ordered by recent creation (proxy for trending)."""
        return (
            self._db.query(SocialPost)
            .order_by(SocialPost.created_at.desc())
            .limit(limit)
            .all()
        )
