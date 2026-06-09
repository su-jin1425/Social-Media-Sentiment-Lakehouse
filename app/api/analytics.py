import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import (
    EngagementOverview,
    TopicListResponse,
    AnalyticsReportResponse,
)
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/engagement", response_model=EngagementOverview)
def get_engagement(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EngagementOverview:
    """Return aggregated engagement metrics overview."""
    service = AnalyticsService(db)
    return service.get_engagement_overview()


@router.get("/topics", response_model=TopicListResponse)
def get_topics(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TopicListResponse:
    """Return top topic clusters ordered by trend score."""
    service = AnalyticsService(db)
    return service.get_topics(limit=limit)


@router.get("/reports", response_model=list[AnalyticsReportResponse])
def get_reports(
    report_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AnalyticsReportResponse]:
    """Return recent analytics reports."""
    service = AnalyticsService(db)
    return service.get_reports(report_type=report_type, limit=limit)
