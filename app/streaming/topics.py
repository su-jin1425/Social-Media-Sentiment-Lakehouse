import logging
from typing import Optional

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

DEFAULT_TOPICS = [
    {"name": "raw_posts", "partitions": 3, "replication_factor": 1},
    {"name": "processed_posts", "partitions": 3, "replication_factor": 1},
    {"name": "sentiment_events", "partitions": 3, "replication_factor": 1},
    {"name": "trend_updates", "partitions": 1, "replication_factor": 1},
    {"name": "analytics_stream", "partitions": 1, "replication_factor": 1},
]


def create_topics(
    topics: Optional[list[dict]] = None,
    broker: Optional[str] = None,
) -> None:
    """Create Kafka topics if they do not already exist."""
    broker = broker or settings.KAFKA_BROKER
    topics = topics or DEFAULT_TOPICS

    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=broker,
            client_id="topic-manager",
        )
    except KafkaError as exc:
        logger.error("Failed to connect to Kafka broker: %s", str(exc))
        return

    new_topics = [
        NewTopic(
            name=t["name"],
            num_partitions=t["partitions"],
            replication_factor=t["replication_factor"],
        )
        for t in topics
    ]

    for topic in new_topics:
        try:
            admin_client.create_topics([topic])
            logger.info("Created topic: %s", topic.name)
        except TopicAlreadyExistsError:
            logger.info("Topic already exists: %s", topic.name)
        except KafkaError as exc:
            logger.error("Failed to create topic %s: %s", topic.name, str(exc))

    admin_client.close()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    create_topics()
