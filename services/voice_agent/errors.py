"""Voice agent service-specific errors."""

from pkg.error_handling.exceptions import AppBaseError


class TokenGenerationError(AppBaseError):
    def __init__(self, message: str = "Failed to generate token") -> None:
        super().__init__(message, status_code=500)


class RoomCreationError(AppBaseError):
    def __init__(self, message: str = "Failed to create room") -> None:
        super().__init__(message, status_code=500)
