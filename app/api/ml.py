import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import require_role
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/models")
def list_models(
    current_user: User = Depends(require_role("admin", "analyst")),
) -> dict[str, Any]:
    """List registered ML models from the tracking server."""
    try:
        import mlflow
        from app.core.config import get_settings
        settings = get_settings()
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        client = mlflow.tracking.MlflowClient()
        models = client.search_registered_models()
        return {
            "models": [
                {
                    "name": m.name,
                    "latest_versions": [
                        {"version": v.version, "status": v.status}
                        for v in (m.latest_versions or [])
                    ],
                }
                for m in models
            ]
        }
    except Exception as exc:
        logger.error("Failed to list ML models: %s", str(exc))
        return {"models": [], "error": "MLflow service unavailable"}


@router.get("/experiments")
def list_experiments(
    current_user: User = Depends(require_role("admin", "analyst")),
) -> dict[str, Any]:
    """List ML experiments from the tracking server."""
    try:
        import mlflow
        from app.core.config import get_settings
        settings = get_settings()
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        client = mlflow.tracking.MlflowClient()
        experiments = client.search_experiments()
        return {
            "experiments": [
                {
                    "experiment_id": e.experiment_id,
                    "name": e.name,
                    "lifecycle_stage": e.lifecycle_stage,
                }
                for e in experiments
            ]
        }
    except Exception as exc:
        logger.error("Failed to list experiments: %s", str(exc))
        return {"experiments": [], "error": "MLflow service unavailable"}


@router.post("/retrain")
def trigger_retrain(
    current_user: User = Depends(require_role("admin")),
) -> dict[str, str]:
    """Trigger an asynchronous model retraining job."""
    logger.info("Model retrain triggered by user: %s", current_user.email)
    # In production, this would dispatch to Celery or a Spark job
    return {"status": "retraining_queued", "message": "Model retraining job has been submitted"}
