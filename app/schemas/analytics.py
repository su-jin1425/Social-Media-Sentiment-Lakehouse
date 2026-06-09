import uuid
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class EngagementOverview(BaseModel):
    """Aggregated engagement metrics overview."""
    total_posts: int
    total_likes: int
    total_comments: int
    total_shares: int
    average_engagement_score: float


class TopicResponse(BaseModel):
    """Schema for a single topic cluster."""
    id: uuid.UUID
    topic_name: str
    keyword_payload: Optional[dict] = None
    trend_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class TopicListResponse(BaseModel):
    """List of topic clusters."""
    topics: list[TopicResponse]


class ViralityMetric(BaseModel):
    """Virality score for a post or topic."""
    entity_id: uuid.UUID
    entity_type: str
    virality_score: float
    engagement_velocity: float


class ViralityResponse(BaseModel):
    """List of virality metrics."""
    items: list[ViralityMetric]


class AnalyticsReportResponse(BaseModel):
    """Schema for an analytics report."""
    id: uuid.UUID
    report_type: str
    generated_payload: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}
