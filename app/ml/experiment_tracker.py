import logging
from typing import Any, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ExperimentTracker:
    """Manages MLflow experiment tracking for sentiment models."""

    def __init__(self, experiment_name: str = "sentiment-classification") -> None:
        self._experiment_name = experiment_name
        self._tracking_uri = settings.MLFLOW_TRACKING_URI

    def _get_client(self):
        """Lazily import and configure MLflow client."""
        import mlflow
        mlflow.set_tracking_uri(self._tracking_uri)
        mlflow.set_experiment(self._experiment_name)
        return mlflow

    def log_training_run(
        self,
        params: dict[str, Any],
        metrics: dict[str, float],
        model_artifact: Optional[Any] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        """Log a training run with parameters, metrics, and optional model artifact."""
        mlflow = self._get_client()
        with mlflow.start_run() as run:
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            if tags:
                mlflow.set_tags(tags)
            if model_artifact:
                mlflow.sklearn.log_model(model_artifact, "model")
            run_id = run.info.run_id
            logger.info("Logged training run: %s", run_id)
            return run_id

    def get_best_run(self, metric_name: str = "accuracy", ascending: bool = False) -> Optional[dict]:
        """Return the best run based on a given metric."""
        mlflow = self._get_client()
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name(self._experiment_name)
        if not experiment:
            logger.warning("Experiment not found: %s", self._experiment_name)
            return None

        order = "ASC" if ascending else "DESC"
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=[f"metrics.{metric_name} {order}"],
            max_results=1,
        )
        if not runs:
            return None

        best = runs[0]
        return {
            "run_id": best.info.run_id,
            "metrics": best.data.metrics,
            "params": best.data.params,
        }

    def list_runs(self, max_results: int = 20) -> list[dict]:
        """List recent experiment runs."""
        mlflow = self._get_client()
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name(self._experiment_name)
        if not experiment:
            return []

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            max_results=max_results,
        )
        return [
            {
                "run_id": r.info.run_id,
                "status": r.info.status,
                "metrics": r.data.metrics,
                "params": r.data.params,
            }
            for r in runs
        ]
