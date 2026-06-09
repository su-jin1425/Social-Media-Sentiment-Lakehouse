from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    EngagementResponse,
    TopicClusterResponse,
    ViralityReport,
)


class AnalyticsService:
    """Service layer for analytics operations."""

    def __init__(self, db: Session) -> None:
        self._repo = AnalyticsRepository(db)

    def get_engagements(
        self, skip: int = 0, limit: int = 50
    ) -> list[EngagementResponse]:
        """Return paginated engagement metrics."""
        results = self._repo.list_engagements(skip=skip, limit=limit)
        return [EngagementResponse.model_validate(r) for r in results]

    def get_topics(
        self, skip: int = 0, limit: int = 50
    ) -> list[TopicClusterResponse]:
        """Return paginated topic clusters."""
        results = self._repo.list_topics(skip=skip, limit=limit)
        return [TopicClusterResponse.model_validate(r) for r in results]

    def get_virality(self, limit: int = 10) -> ViralityReport:
        """Generate a virality report from engagement data."""
        top_posts = self._repo.get_virality_data(limit=limit)
        avg_engagement = self._repo.get_average_engagement()
        return ViralityReport(
            top_posts=top_posts,
            average_engagement=avg_engagement,
        )
