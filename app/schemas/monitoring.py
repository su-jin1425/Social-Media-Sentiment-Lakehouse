from datetime import datetime
from typing import Any

from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Schema for system health check response."""
    status: str
    database: str
    redis: str
    kafka: str
    timestamp: datetime


class PipelineMetrics(BaseModel):
    """Schema for streaming pipeline metrics."""
    kafka_throughput: float
    spark_latency: float
    processing_rate: float
    timestamp: datetime


class PipelineStatusResponse(BaseModel):
    """Schema for overall pipeline status."""
    kafka_status: str
    spark_status: str
    delta_lake_status: str
    active_consumers: int
    pending_messages: int
