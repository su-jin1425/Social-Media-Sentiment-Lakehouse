import logging
from typing import Optional

from pyspark.sql import SparkSession

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def create_spark_session(
    app_name: str = "SentimentLakehouse",
    master: Optional[str] = None,
) -> SparkSession:
    """Create and return a configured SparkSession with Delta Lake support."""
    master = master or settings.SPARK_MASTER

    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(master)
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .config("spark.sql.adaptive.enabled", "true")
    )

    session = builder.getOrCreate()
    logger.info("SparkSession created: app=%s, master=%s", app_name, master)
    return session
