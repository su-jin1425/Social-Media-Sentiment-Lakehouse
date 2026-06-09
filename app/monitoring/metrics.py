import logging

from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger(__name__)

instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=False,
    excluded_handlers=["/metrics", "/health"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
)


def setup_metrics(app) -> None:
    """Instrument the FastAPI application with Prometheus metrics."""
    instrumentator.instrument(app).expose(
        app, include_in_schema=False, should_gzip=True
    )
    logger.info("Prometheus metrics endpoint configured at /metrics")
