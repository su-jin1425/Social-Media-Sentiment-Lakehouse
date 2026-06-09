import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql://postgres:password@db:5432/sentiment_db"
    REDIS_URL: str = "redis://redis:6379"
    SECRET_KEY: str = "change_this_to_a_secure_random_string_in_production"
    KAFKA_BROKER: str = "kafka:9092"
    SPARK_MASTER: str = "spark://spark-master:7077"
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    ALGORITHM: str = "HS256"

    API_RATE_LIMIT: int = 100  # requests per minute

    KAFKA_TOPICS: dict = {
        "raw_posts": "raw_posts",
        "processed_posts": "processed_posts",
        "sentiment_events": "sentiment_events",
        "trend_updates": "trend_updates",
        "analytics_stream": "analytics_stream",
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
