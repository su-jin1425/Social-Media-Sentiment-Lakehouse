import logging
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Global exception handler that converts AppException subclasses to JSON responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Catch application and unhandled exceptions and return structured JSON."""
        try:
            response = await call_next(request)
            return response
        except AppException as exc:
            logger.warning(
                "Application error: status=%d detail=%s", exc.status_code, exc.detail
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        except Exception as exc:
            logger.exception("Unhandled exception: %s", str(exc))
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
