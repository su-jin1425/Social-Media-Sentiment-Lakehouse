import uuid
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.engagement_metric import EngagementMetric
from app.models.topic_cluster import TopicCluster
from app.models.analytics_report import AnalyticsReport


class AnalyticsRepository:
    """Data access layer for analytics-related entities."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_engagement_overview(self) -> dict:
        """Return aggregated engagement metrics."""
        result = self._db.query(
            func.count(EngagementMetric.id).label("total_posts"),
            func.coalesce(func.sum(EngagementMetric.likes), 0).label("total_likes"),
            func.coalesce(func.sum(EngagementMetric.comments), 0).label("total_comments"),
            func.coalesce(func.sum(EngagementMetric.shares), 0).label("total_shares"),
            func.coalesce(func.avg(EngagementMetric.engagement_score), 0.0).label(
                "average_engagement_score"
            ),
        ).first()
        return {
            "total_posts": int(result.total_posts),
            "total_likes": int(result.total_likes),
            "total_comments": int(result.total_comments),
            "total_shares": int(result.total_shares),
            "average_engagement_score": round(float(result.average_engagement_score), 4),
        }

    def get_topics(self, limit: int = 20) -> list[TopicCluster]:
        """Return top topic clusters ordered by trend score."""
        return (
            self._db.query(TopicCluster)
            .order_by(TopicCluster.trend_score.desc())
            .limit(limit)
            .all()
        )

    def create_topic(self, topic: TopicCluster) -> TopicCluster:
        """Persist a new topic cluster."""
        self._db.add(topic)
        self._db.commit()
        self._db.refresh(topic)
        return topic

    def create_report(self, report: AnalyticsReport) -> AnalyticsReport:
        """Persist a new analytics report."""
        self._db.add(report)
        self._db.commit()
        self._db.refresh(report)
        return report

    def get_reports(self, report_type: Optional[str] = None, limit: int = 20) -> list[AnalyticsReport]:
        """Return recent analytics reports, optionally filtered by type."""
        query = self._db.query(AnalyticsReport)
        if report_type:
            query = query.filter(AnalyticsReport.report_type == report_type)
        return query.order_by(AnalyticsReport.created_at.desc()).limit(limit).all()
