from sqlalchemy.orm import Session

from app.repositories.sentiment_repository import SentimentRepository
from app.schemas.sentiment import (
    SentimentOverview,
    SentimentTrend,
    PlatformSentiment,
)


class SentimentService:
    """Service layer for sentiment analytics operations."""

    def __init__(self, db: Session) -> None:
        self._repo = SentimentRepository(db)

    def get_overview(self) -> SentimentOverview:
        """Return an aggregated sentiment overview."""
        data = self._repo.get_overview()
        return SentimentOverview(**data)

    def get_trends(self, days: int = 7) -> list[SentimentTrend]:
        """Return sentiment trends over the specified number of days."""
        data = self._repo.get_trends(days=days)
        return [SentimentTrend(**entry) for entry in data]

    def get_by_platform(self) -> list[PlatformSentiment]:
        """Return sentiment distribution grouped by platform."""
        data = self._repo.get_by_platform()
        return [PlatformSentiment(**entry) for entry in data]
