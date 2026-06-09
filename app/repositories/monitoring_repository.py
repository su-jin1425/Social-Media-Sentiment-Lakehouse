from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.monitoring_metric import MonitoringMetric


class MonitoringRepository:
    """Data access layer for monitoring metrics."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, metric: MonitoringMetric) -> MonitoringMetric:
        """Persist a new monitoring metric."""
        self._db.add(metric)
        self._db.commit()
        self._db.refresh(metric)
        return metric

    def get_latest(self, limit: int = 10) -> list[MonitoringMetric]:
        """Return the most recent monitoring metrics."""
        return (
            self._db.query(MonitoringMetric)
            .order_by(MonitoringMetric.created_at.desc())
            .limit(limit)
            .all()
        )
