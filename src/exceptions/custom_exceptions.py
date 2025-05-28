from typing import Optional


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseError(AppException):
    def __init__(
        self, message: str, details: Optional[str] = None, status_code: int = 500
    ):
        self.details = details
        super().__init__(message, status_code)


class ValidationError(AppException):
    def __init__(
        self, message: str, details: Optional[str] = None, status_code: int = 400
    ):
        self.details = details
        super().__init__(message, status_code)
