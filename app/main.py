import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.utils.logging_config import configure_logging
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.exception_handler import ExceptionHandlerMiddleware
from app.monitoring.metrics import setup_metrics
from app.api import auth, posts, sentiment, analytics, monitoring, ml

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title="Social Media Sentiment Lakehouse",
    description="Enterprise-grade distributed sentiment analytics platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# -- Middleware (order matters: outermost first) --
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(RateLimiterMiddleware)

# -- Prometheus instrumentation --
setup_metrics(app)

# -- Register API routers --
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(sentiment.router)
app.include_router(analytics.router)
app.include_router(monitoring.router)
app.include_router(ml.router)


@app.get("/", tags=["Root"])
def root() -> dict:
    """Root endpoint returning platform metadata."""
    return {
        "service": "Social Media Sentiment Lakehouse",
        "status": "operational",
        "documentation": "/docs",
    }


logger.info("Application initialized successfully")
