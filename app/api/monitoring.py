import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.monitoring import HealthCheckResponse, PipelineMetrics
from app.services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)) -> HealthCheckResponse:
    """Return system health status for database, Redis, and Kafka."""
    service = MonitoringService(db)
    return service.health_check()


@router.get("/metrics", response_model=list[PipelineMetrics])
def get_metrics(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PipelineMetrics]:
    """Return recent pipeline monitoring metrics."""
    service = MonitoringService(db)
    return service.get_latest_metrics(limit=limit)
