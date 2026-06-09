import json
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError

from app.core.config import get_settings
from app.core.logging import logger

PLATFORMS = ["twitter", "reddit", "instagram", "youtube"]

SAMPLE_CONTENT = [
    "This product is absolutely fantastic, exceeded all my expectations.",
    "Terrible customer service experience. Will never use again.",
    "Just saw the latest announcement. Seems interesting but need more details.",
    "The new update broke everything. Frustrated beyond belief.",
    "Great value for money. Highly recommend to everyone.",
    "Average experience, nothing special. Could be better.",
    "Love the design and user interface, very intuitive.",
    "Misleading advertising. The product does not match the description.",
    "Neutral on this one. Waiting for more reviews before deciding.",
    "Outstanding quality and fast shipping. Very impressed.",
    "The worst purchase I have ever made. Complete waste of money.",
    "Solid performance and reliable. Been using it daily without issues.",
    "Overpriced for what it offers. There are better alternatives.",
    "Support team was very helpful and resolved my issue quickly.",
    "Buggy software with constant crashes. Needs serious improvement.",
    "Good product overall. Minor issues but nothing deal-breaking.",
    "Absolutely love the new features in the latest release.",
    "Poor quality materials. Started falling apart after a week.",
    "Not bad, not great. Just okay for everyday use.",
    "Five stars across the board. Best in class.",
]

SAMPLE_AUTHORS = [
    "alex_johnson", "maria_garcia", "james_smith", "priya_patel",
    "chen_wei", "sarah_williams", "omar_hassan", "yuki_tanaka",
    "david_brown", "fatima_ali", "lucas_silva", "emma_jones",
    "raj_kumar", "anna_muller", "carlos_rodriguez", "liu_yang",
]


def _generate_post() -> dict:
    """Generate a single synthetic social media post payload."""
    return {
        "id": str(uuid.uuid4()),
        "platform": random.choice(PLATFORMS),
        "author_name": random.choice(SAMPLE_AUTHORS),
        "content": random.choice(SAMPLE_CONTENT),
        "likes": random.randint(0, 5000),
        "comments": random.randint(0, 500),
        "shares": random.randint(0, 1000),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


class SocialMediaProducer:
    """Kafka producer that simulates streaming social media data ingestion.

    In production, this would be replaced by connectors to real social
    media platform APIs (Twitter/X, Reddit, Instagram, YouTube).
    """

    def __init__(self, topic: str = "raw_posts") -> None:
        settings = get_settings()
        self._topic = topic
        self._producer: Optional[KafkaProducer] = None
        self._broker = settings.KAFKA_BROKER

    def _connect(self) -> None:
        """Establish connection to the Kafka broker."""
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self._broker,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                retry_backoff_ms=500,
                max_in_flight_requests_per_connection=1,
            )
            logger.info("Kafka producer connected to broker: %s", self._broker)

    def produce(self, count: int = 1) -> int:
        """Produce synthetic social media posts to the configured Kafka topic.

        Args:
            count: Number of posts to produce.

        Returns:
            Number of posts successfully published.
        """
        self._connect()
        published = 0
        for _ in range(count):
            post = _generate_post()
            try:
                self._producer.send(
                    self._topic,
                    key=post["platform"],
                    value=post,
                )
                published += 1
            except KafkaError as exc:
                logger.error("Failed to publish post to Kafka: %s", str(exc))

        self._producer.flush()
        logger.info(
            "Published %d/%d posts to topic '%s'", published, count, self._topic
        )
        return published

    def run_continuous(self, interval_seconds: float = 1.0, batch_size: int = 5) -> None:
        """Run the producer in a continuous loop.

        Args:
            interval_seconds: Delay between each batch.
            batch_size: Number of posts per batch.
        """
        logger.info(
            "Starting continuous producer: batch_size=%d, interval=%.1fs",
            batch_size,
            interval_seconds,
        )
        try:
            while True:
                self.produce(count=batch_size)
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Producer interrupted, shutting down")
        finally:
            self.close()

    def close(self) -> None:
        """Flush and close the Kafka producer."""
        if self._producer:
            self._producer.flush()
            self._producer.close()
            self._producer = None
            logger.info("Kafka producer closed")
