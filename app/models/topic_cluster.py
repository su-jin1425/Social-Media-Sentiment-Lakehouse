import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TopicCluster(Base):
    """Represents a detected topic cluster from social media analysis."""

    __tablename__ = "topic_clusters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    keyword_payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    trend_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
