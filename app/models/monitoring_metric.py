import uuid
from datetime import datetime, timezone

from sqlalchemy import Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class MonitoringMetric(Base):
    """Stores pipeline performance and system health metrics."""

    __tablename__ = "monitoring_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    kafka_throughput: Mapped[float] = mapped_column(Float, default=0.0)
    spark_latency: Mapped[float] = mapped_column(Float, default=0.0)
    processing_rate: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
