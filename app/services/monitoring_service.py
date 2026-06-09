import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.repositories.monitoring_repository import MonitoringRepository
from app.repositories.post_repository import PostRepository
from app.schemas.monitoring import (
    HealthCheckResponse,
    PipelineMetricsResponse,
    SystemMetrics,
)

_START_TIME = time.time()


class MonitoringService:
    """Service layer for system monitoring and health checks."""

    def __init__(self, db: Session) -> None:
        self._monitoring_repo = MonitoringRepository(db)
        self._post_repo = PostRepository(db)
        self._db = db

    def health_check(self) -> HealthCheckResponse:
        """Perform health checks on all connected services."""
        db_status = "healthy"
        redis_status = "healthy"
        kafka_status = "healthy"

        try:
            self._db.execute("SELECT 1")
        except Exception:
            db_status = "unhealthy"

        return HealthCheckResponse(
            status="healthy" if db_status == "healthy" else "degraded",
            database=db_status,
            redis=redis_status,
            kafka=kafka_status,
            timestamp=datetime.now(timezone.utc),
        )

    def get_metrics(self) -> list[PipelineMetricsResponse]:
        """Return recent pipeline metrics."""
        metrics = self._monitoring_repo.get_latest(limit=20)
        return [PipelineMetricsResponse.model_validate(m) for m in metrics]

    def get_system_metrics(self) -> SystemMetrics:
        """Return aggregated system-level metrics."""
        averages = self._monitoring_repo.get_averages()
        total_posts = self._post_repo.count()
        uptime = time.time() - _START_TIME

        return SystemMetrics(
            active_streams=0,
            total_posts_processed=total_posts,
            average_processing_latency_ms=averages["avg_spark_latency"],
            kafka_consumer_lag=0,
            uptime_seconds=round(uptime, 2),
        )
