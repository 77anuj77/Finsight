"""
Custom FastAPI Exceptions
Provides type-safe exception classes with context-specific messages.
"""
from fastapi import HTTPException


class FinSightHTTPException(HTTPException):
    """Base exception for FinSight application errors."""

    def __init__(self, status_code: int, detail: str, type: str = "error", **extra_data):
        super().__init__(status_code=status_code, detail=detail)
        self.type = type
        self.extra_data = extra_data


class BadRequestException(FinSightHTTPException):
    """Bad request (422)."""
    def __init__(self, detail: str = "Bad request", **extra_data):
        super().__init__(status_code=422, detail=detail, type="bad_request", **extra_data)


class UnauthorizedException(FinSightHTTPException):
    """Unauthorized (401)."""
    def __init__(self, detail: str = "Unauthorized", **extra_data):
        super().__init__(status_code=401, detail=detail, type="unauthorized", **extra_data)


class ForbiddenException(FinSightHTTPException):
    """Forbidden (403)."""
    def __init__(self, detail: str = "Forbidden", **extra_data):
        super().__init__(status_code=403, detail=detail, type="forbidden", **extra_data)


class NotFoundException(FinSightHTTPException):
    """Resource not found (404)."""
    def __init__(self, detail: str = "Resource not found", resource_type: str = None, **extra_data):
        super().__init__(status_code=404, detail=detail, type="not_found", **extra_data)
        if resource_type:
            self.extra_data["resource_type"] = resource_type


class ConflictException(FinSightHTTPException):
    """Conflict (409) - e.g., duplicate entry."""
    def __init__(self, detail: str = "Conflict", **extra_data):
        super().__init__(status_code=409, detail=detail, type="conflict", **extra_data)


class ValidationException(FinSightHTTPException):
    """Validation error (400)."""
    def __init__(self, detail: str = "Validation failed", **extra_data):
        super().__init__(status_code=400, detail=detail, type="validation", **extra_data)


class OverdraftException(FinSightHTTPException):
    """Insufficient balance error (400)."""
    def __init__(self, detail: str = "Insufficient balance", account_id: str = None, **extra_data):
        super().__init__(status_code=400, detail=detail, type="overdraft", **extra_data)
        if account_id:
            self.extra_data["account_id"] = account_id


class DuplicateEntryException(ConflictException):
    """Duplicate entry error (409)."""
    def __init__(self, detail: str = "Entry already exists", field: str = None, **extra_data):
        super().__init__(detail=detail, type="duplicate", **extra_data)
        if field:
            self.extra_data["field"] = field