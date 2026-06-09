from typing import Any, Optional


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        status_code: int = 500,
        detail: str = "Internal server error",
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(self.detail)


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(status_code=401, detail=detail)


class AuthorizationError(AppException):
    """Raised when user lacks required permissions."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(status_code=403, detail=detail)


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=404, detail=detail)


class ConflictError(AppException):
    """Raised when a resource already exists or a conflict occurs."""

    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(status_code=409, detail=detail)


class ValidationError(AppException):
    """Raised when request validation fails beyond Pydantic defaults."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(status_code=422, detail=detail)


class RateLimitError(AppException):
    """Raised when a client exceeds the configured rate limit."""

    def __init__(self, detail: str = "Rate limit exceeded") -> None:
        super().__init__(status_code=429, detail=detail)


class StreamingError(AppException):
    """Raised when a Kafka or streaming pipeline operation fails."""

    def __init__(self, detail: str = "Streaming pipeline error") -> None:
        super().__init__(status_code=503, detail=detail)
