import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import func, case, cast, Date
from sqlalchemy.orm import Session

from app.models.sentiment_score import SentimentScore
from app.models.social_post import SocialPost


class SentimentRepository:
    """Data access layer for SentimentScore entities."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, score: SentimentScore) -> SentimentScore:
        """Persist a new sentiment score."""
        self._db.add(score)
        self._db.commit()
        self._db.refresh(score)
        return score

    def create_batch(self, scores: list[SentimentScore]) -> list[SentimentScore]:
        """Persist a batch of sentiment scores."""
        self._db.add_all(scores)
        self._db.commit()
        return scores

    def get_overview(self) -> dict:
        """Return aggregated sentiment counts and ratios."""
        total = self._db.query(func.count(SentimentScore.id)).scalar() or 0
        if total == 0:
            return {
                "total_analyzed": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 0.0,
                "average_confidence": 0.0,
            }
        positive = (
            self._db.query(func.count(SentimentScore.id))
            .filter(SentimentScore.sentiment_label == "positive")
            .scalar()
            or 0
        )
        negative = (
            self._db.query(func.count(SentimentScore.id))
            .filter(SentimentScore.sentiment_label == "negative")
            .scalar()
            or 0
        )
        neutral = (
            self._db.query(func.count(SentimentScore.id))
            .filter(SentimentScore.sentiment_label == "neutral")
            .scalar()
            or 0
        )
        avg_conf = (
            self._db.query(func.avg(SentimentScore.confidence_score)).scalar() or 0.0
        )
        return {
            "total_analyzed": total,
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "positive_ratio": round(positive / total, 4),
            "negative_ratio": round(negative / total, 4),
            "neutral_ratio": round(neutral / total, 4),
            "average_confidence": round(float(avg_conf), 4),
        }

    def get_trends(self, days: int = 30) -> list[dict]:
        """Return daily sentiment counts for the past N days."""
        results = (
            self._db.query(
                cast(SentimentScore.processed_at, Date).label("period"),
                func.sum(
                    case(
                        (SentimentScore.sentiment_label == "positive", 1), else_=0
                    )
                ).label("positive"),
                func.sum(
                    case(
                        (SentimentScore.sentiment_label == "negative", 1), else_=0
                    )
                ).label("negative"),
                func.sum(
                    case(
                        (SentimentScore.sentiment_label == "neutral", 1), else_=0
                    )
                ).label("neutral"),
            )
            .group_by(cast(SentimentScore.processed_at, Date))
            .order_by(cast(SentimentScore.processed_at, Date).desc())
            .limit(days)
            .all()
        )
        return [
            {
                "period": str(r.period),
                "positive": int(r.positive),
                "negative": int(r.negative),
                "neutral": int(r.neutral),
            }
            for r in results
        ]

    def get_by_platform(self) -> list[dict]:
        """Return sentiment counts grouped by platform."""
        results = (
            self._db.query(
                SocialPost.platform,
                func.sum(
                    case(
                        (SentimentScore.sentiment_label == "positive", 1), else_=0
                    )
                ).label("positive"),
                func.sum(
                    case(
                        (SentimentScore.sentiment_label == "negative", 1), else_=0
                    )
                ).label("negative"),
                func.sum(
                    case(
                        (SentimentScore.sentiment_label == "neutral", 1), else_=0
                    )
                ).label("neutral"),
                func.count(SentimentScore.id).label("total"),
            )
            .join(SocialPost, SentimentScore.post_id == SocialPost.id)
            .group_by(SocialPost.platform)
            .all()
        )
        return [
            {
                "platform": r.platform,
                "positive": int(r.positive),
                "negative": int(r.negative),
                "neutral": int(r.neutral),
                "total": int(r.total),
            }
            for r in results
        ]
