import time
import logging
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter middleware for API endpoints."""

    def __init__(self, app: Callable, requests_per_minute: int = 0) -> None:
        super().__init__(app)
        self._requests_per_minute = requests_per_minute or settings.API_RATE_LIMIT
        self._clients: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before passing request to the next handler."""
        client_ip: str = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60.0

        # Clean old entries
        self._clients[client_ip] = [
            ts for ts in self._clients[client_ip] if ts > window_start
        ]

        if len(self._clients[client_ip]) >= self._requests_per_minute:
            logger.warning("Rate limit exceeded for client: %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        self._clients[client_ip].append(now)
        response: Response = await call_next(request)
        return response
