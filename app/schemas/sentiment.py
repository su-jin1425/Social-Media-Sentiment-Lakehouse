import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SentimentScoreResponse(BaseModel):
    """Schema for a single sentiment score result."""
    id: uuid.UUID
    post_id: uuid.UUID
    sentiment_label: str
    confidence_score: float
    model_version: Optional[str] = None
    processed_at: datetime

    model_config = {"from_attributes": True}


class SentimentOverview(BaseModel):
    """Aggregated sentiment overview across all posts."""
    total_analyzed: int
    positive_count: int
    negative_count: int
    neutral_count: int
    positive_ratio: float
    negative_ratio: float
    neutral_ratio: float
    average_confidence: float


class SentimentTrend(BaseModel):
    """Sentiment counts bucketed by time period."""
    period: str
    positive: int
    negative: int
    neutral: int


class SentimentTrendsResponse(BaseModel):
    """List of sentiment trends over time."""
    trends: list[SentimentTrend]


class PlatformSentiment(BaseModel):
    """Sentiment breakdown for a single platform."""
    platform: str
    positive: int
    negative: int
    neutral: int
    total: int


class SentimentByPlatformResponse(BaseModel):
    """Sentiment breakdown grouped by platform."""
    platforms: list[PlatformSentiment]
