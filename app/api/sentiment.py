import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.sentiment import (
    SentimentOverview,
    SentimentTrendsResponse,
    SentimentByPlatformResponse,
)
from app.services.sentiment_service import SentimentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sentiment", tags=["Sentiment Analytics"])


@router.get("/overview", response_model=SentimentOverview)
def get_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SentimentOverview:
    """Return aggregated sentiment overview across all analyzed posts."""
    service = SentimentService(db)
    return service.get_overview()


@router.get("/trends", response_model=SentimentTrendsResponse)
def get_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SentimentTrendsResponse:
    """Return daily sentiment trends for the specified number of days."""
    service = SentimentService(db)
    return service.get_trends(days=days)


@router.get("/platforms", response_model=SentimentByPlatformResponse)
def get_by_platform(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SentimentByPlatformResponse:
    """Return sentiment breakdown grouped by social media platform."""
    service = SentimentService(db)
    return service.get_by_platform()
