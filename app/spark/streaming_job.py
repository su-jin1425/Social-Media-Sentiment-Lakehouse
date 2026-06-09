import logging
from typing import Optional

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType

from app.spark.session import create_spark_session
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Schema for raw social media posts from Kafka
RAW_POST_SCHEMA = StructType([
    StructField("id", StringType(), True),
    StructField("platform", StringType(), True),
    StructField("author_name", StringType(), True),
    StructField("content", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("metadata", StructType([
        StructField("likes", IntegerType(), True),
        StructField("comments", IntegerType(), True),
        StructField("shares", IntegerType(), True),
    ]), True),
])

POSITIVE_KEYWORDS = [
    "incredible", "excellent", "impressive", "loving", "great",
    "solid", "seamless", "promising", "helpful", "best",
]
NEGATIVE_KEYWORDS = [
    "unresponsive", "unacceptable", "outage", "frustrating", "broken",
    "disappointing", "crashes", "vulnerability", "irrelevant", "outdated",
]


def classify_sentiment_udf(content: str) -> str:
    """Simple keyword-based sentiment classification."""
    if not content:
        return "neutral"
    lower = content.lower()
    pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in lower)
    neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in lower)
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    return "neutral"


def build_bronze_stream(spark: SparkSession, kafka_broker: str) -> DataFrame:
    """Read raw data from Kafka and parse JSON payloads."""
    raw_stream = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", kafka_broker)
        .option("subscribe", "raw_posts")
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .load()
    )

    parsed = (
        raw_stream
        .selectExpr("CAST(value AS STRING) as json_str")
        .select(F.from_json(F.col("json_str"), RAW_POST_SCHEMA).alias("data"))
        .select("data.*")
    )
    return parsed


def build_silver_stream(bronze_df: DataFrame) -> DataFrame:
    """Clean and enrich the bronze dataframe."""
    sentiment_udf = F.udf(classify_sentiment_udf, StringType())

    silver = (
        bronze_df
        .withColumn("content_cleaned", F.trim(F.lower(F.col("content"))))
        .withColumn("word_count", F.size(F.split(F.col("content"), " ")))
        .withColumn("sentiment_label", sentiment_udf(F.col("content")))
        .withColumn("processed_at", F.current_timestamp())
        .withColumn("likes", F.col("metadata.likes"))
        .withColumn("comments", F.col("metadata.comments"))
        .withColumn("shares", F.col("metadata.shares"))
        .withColumn(
            "engagement_score",
            (F.col("likes") + F.col("comments") * 2 + F.col("shares") * 3).cast(FloatType()),
        )
        .drop("metadata")
    )
    return silver


def build_gold_aggregation(silver_df: DataFrame) -> DataFrame:
    """Create windowed aggregations for analytics."""
    gold = (
        silver_df
        .withWatermark("processed_at", "5 minutes")
        .groupBy(
            F.window(F.col("processed_at"), "5 minutes"),
            F.col("platform"),
            F.col("sentiment_label"),
        )
        .agg(
            F.count("*").alias("post_count"),
            F.avg("engagement_score").alias("avg_engagement"),
            F.sum("likes").alias("total_likes"),
            F.sum("comments").alias("total_comments"),
            F.sum("shares").alias("total_shares"),
        )
    )
    return gold


def run_streaming_pipeline(
    delta_base_path: str = "/data/delta",
    checkpoint_base_path: str = "/data/checkpoint",
) -> None:
    """Execute the full Bronze -> Silver -> Gold streaming pipeline."""
    spark = create_spark_session()
    kafka_broker = settings.KAFKA_BROKER

    bronze_df = build_bronze_stream(spark, kafka_broker)
    silver_df = build_silver_stream(bronze_df)
    gold_df = build_gold_aggregation(silver_df)

    # Write Bronze layer
    bronze_query = (
        bronze_df.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{checkpoint_base_path}/bronze")
        .start(f"{delta_base_path}/bronze")
    )
    logger.info("Bronze stream started")

    # Write Silver layer
    silver_query = (
        silver_df.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{checkpoint_base_path}/silver")
        .start(f"{delta_base_path}/silver")
    )
    logger.info("Silver stream started")

    # Write Gold layer
    gold_query = (
        gold_df.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{checkpoint_base_path}/gold")
        .start(f"{delta_base_path}/gold")
    )
    logger.info("Gold stream started")

    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    run_streaming_pipeline()
