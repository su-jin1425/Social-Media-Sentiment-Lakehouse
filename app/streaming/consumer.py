import json
import logging
from typing import Optional

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.social_post import SocialPost
from app.models.engagement_metric import EngagementMetric
from app.repositories.post_repository import PostRepository

logger = logging.getLogger(__name__)
settings = get_settings()


def create_consumer(
    topic: str = "raw_posts",
    group_id: str = "lakehouse-consumer-group",
) -> KafkaConsumer:
    """Create and return a configured Kafka consumer instance."""
    return KafkaConsumer(
        topic,
        bootstrap_servers=settings.KAFKA_BROKER,
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        auto_commit_interval_ms=5000,
        max_poll_records=100,
    )


def process_message(data: dict, db: Session) -> None:
    """Process a single Kafka message and persist it to PostgreSQL."""
    try:
        post = SocialPost(
            platform=data.get("platform", "unknown"),
            author_name=data.get("author_name", "anonymous"),
            content=data.get("content", ""),
            source_id=data.get("id"),
        )
        db.add(post)
        db.flush()

        metadata = data.get("metadata", {})
        likes = metadata.get("likes", 0)
        comments = metadata.get("comments", 0)
        shares = metadata.get("shares", 0)
        total = likes + comments * 2 + shares * 3
        engagement = EngagementMetric(
            post_id=post.id,
            likes=likes,
            comments=comments,
            shares=shares,
            engagement_score=float(total),
        )
        db.add(engagement)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("Failed to process message: %s", str(exc))


def run_consumer(
    topic: str = "raw_posts",
    group_id: str = "lakehouse-consumer-group",
) -> None:
    """Run the Kafka consumer loop, persisting messages to the database."""
    consumer = create_consumer(topic=topic, group_id=group_id)
    logger.info("Consumer started: topic=%s, group=%s", topic, group_id)
    consumed_count = 0

    try:
        for message in consumer:
            db = SessionLocal()
            try:
                process_message(message.value, db)
                consumed_count += 1
                if consumed_count % 100 == 0:
                    logger.info("Consumed %d messages", consumed_count)
            finally:
                db.close()
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    finally:
        consumer.close()
        logger.info("Consumer closed. Total messages consumed: %d", consumed_count)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_consumer()
