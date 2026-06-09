import logging
from typing import Optional
from dataclasses import dataclass

from app.sentiment.nlp import preprocess

logger = logging.getLogger(__name__)

POSITIVE_LEXICON = {
    "incredible": 0.9, "excellent": 0.9, "impressive": 0.8, "loving": 0.8,
    "great": 0.7, "solid": 0.6, "seamless": 0.8, "promising": 0.7,
    "helpful": 0.7, "best": 0.8, "good": 0.6, "amazing": 0.9,
    "perfect": 0.9, "improved": 0.6, "well": 0.5, "outstanding": 0.9,
}

NEGATIVE_LEXICON = {
    "unresponsive": -0.8, "unacceptable": -0.9, "outage": -0.7,
    "frustrating": -0.8, "broken": -0.8, "disappointing": -0.7,
    "crashes": -0.8, "vulnerability": -0.7, "irrelevant": -0.6,
    "outdated": -0.6, "terrible": -0.9, "awful": -0.9, "worst": -0.9,
    "failed": -0.7, "bad": -0.6, "poor": -0.6, "horrible": -0.9,
}


@dataclass
class SentimentResult:
    """Container for sentiment analysis output."""
    label: str
    score: float
    confidence: float
    positive_score: float
    negative_score: float


class SentimentAnalyzer:
    """Lexicon-based sentiment analyzer with confidence scoring."""

    def __init__(
        self,
        positive_lexicon: Optional[dict[str, float]] = None,
        negative_lexicon: Optional[dict[str, float]] = None,
    ) -> None:
        self._positive = positive_lexicon or POSITIVE_LEXICON
        self._negative = negative_lexicon or NEGATIVE_LEXICON

    def analyze(self, text: str) -> SentimentResult:
        """Analyze the sentiment of the given text."""
        processed = preprocess(text)
        words = processed.split()

        pos_score = 0.0
        neg_score = 0.0
        matched_count = 0

        for word in words:
            if word in self._positive:
                pos_score += self._positive[word]
                matched_count += 1
            elif word in self._negative:
                neg_score += abs(self._negative[word])
                matched_count += 1

        total_score = pos_score - neg_score

        if matched_count == 0:
            confidence = 0.5
        else:
            confidence = min(matched_count / max(len(words), 1), 1.0)

        if total_score > 0.1:
            label = "positive"
        elif total_score < -0.1:
            label = "negative"
        else:
            label = "neutral"

        return SentimentResult(
            label=label,
            score=round(total_score, 4),
            confidence=round(confidence, 4),
            positive_score=round(pos_score, 4),
            negative_score=round(neg_score, 4),
        )

    def analyze_batch(self, texts: list[str]) -> list[SentimentResult]:
        """Analyze sentiment for a batch of texts."""
        return [self.analyze(t) for t in texts]
