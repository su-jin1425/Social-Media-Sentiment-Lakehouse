import logging
import numpy as np
from typing import Any, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from app.ml.experiment_tracker import ExperimentTracker
from app.sentiment.nlp import preprocess

logger = logging.getLogger(__name__)


class SentimentModelTrainer:
    """Trains and evaluates a sentiment classification model using TF-IDF and LogisticRegression."""

    def __init__(
        self,
        max_features: int = 5000,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> None:
        self._max_features = max_features
        self._test_size = test_size
        self._random_state = random_state
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._model: Optional[LogisticRegression] = None
        self._tracker = ExperimentTracker()

    def train(
        self,
        texts: list[str],
        labels: list[str],
        log_to_mlflow: bool = True,
    ) -> dict[str, float]:
        """Train a sentiment classification model and return evaluation metrics."""
        processed_texts = [preprocess(t) for t in texts]

        self._vectorizer = TfidfVectorizer(
            max_features=self._max_features,
            ngram_range=(1, 2),
        )
        X = self._vectorizer.fit_transform(processed_texts)

        X_train, X_test, y_train, y_test = train_test_split(
            X, labels,
            test_size=self._test_size,
            random_state=self._random_state,
            stratify=labels,
        )

        self._model = LogisticRegression(
            max_iter=1000,
            multi_class="multinomial",
            solver="lbfgs",
            random_state=self._random_state,
        )
        self._model.fit(X_train, y_train)

        y_pred = self._model.predict(X_test)
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
            "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
            "f1": f1_score(y_test, y_pred, average="weighted", zero_division=0),
        }

        logger.info("Model trained: accuracy=%.4f, f1=%.4f", metrics["accuracy"], metrics["f1"])

        if log_to_mlflow:
            try:
                params = {
                    "max_features": self._max_features,
                    "test_size": self._test_size,
                    "model_type": "LogisticRegression",
                    "ngram_range": "1,2",
                }
                self._tracker.log_training_run(
                    params=params,
                    metrics=metrics,
                    model_artifact=self._model,
                    tags={"pipeline": "sentiment-classification"},
                )
            except Exception as exc:
                logger.warning("Failed to log to MLflow: %s", str(exc))

        return metrics

    def predict(self, texts: list[str]) -> list[str]:
        """Predict sentiment labels for a list of texts."""
        if not self._model or not self._vectorizer:
            raise RuntimeError("Model has not been trained yet")
        processed = [preprocess(t) for t in texts]
        X = self._vectorizer.transform(processed)
        return list(self._model.predict(X))
