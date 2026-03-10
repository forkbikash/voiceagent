"""Custom exception hierarchy."""


class AppBaseError(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationError(AppBaseError):
    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message, status_code=422)


class NotFoundError(AppBaseError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)
