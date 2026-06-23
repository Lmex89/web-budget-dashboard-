"""
Application exception hierarchy.

Follows SOLID principles:
- Each domain has its own exception class
- Exceptions are granular and specific
- Base class provides standardized JSON serialization
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings


class AppException(Exception):
    """Base application exception - all custom exceptions inherit from this."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


#
# ─── HTTP Shortcuts ───────────────────────────────────────────────────────────
#

class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: str | int):
        super().__init__(
            code="ERR_NOT_FOUND",
            message=f"{resource} with id '{resource_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required."):
        super().__init__(
            code="ERR_UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self):
        super().__init__("Invalid email or password.")
        self.code = "ERR_INVALID_CREDENTIALS"


class ForbiddenException(AppException):
    def __init__(self, message: str = "Access denied."):
        super().__init__(
            code="ERR_FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ValidationException(AppException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            code="ERR_VALIDATION",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__(
            code="ERR_CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class EmailAlreadyRegisteredException(ConflictException):
    def __init__(self, email: str):
        super().__init__(f"A user with email '{email}' is already registered.")


#
# ─── Expense Exceptions ──────────────────────────────────────────────────────
#

class CategoryNotFoundException(NotFoundException):
    def __init__(self, category_id: str):
        super().__init__("Category", category_id)


class ExpenseNotFoundException(NotFoundException):
    def __init__(self, expense_id: str):
        super().__init__("Expense", expense_id)


class ExpenseNotInFamilyException(ForbiddenException):
    def __init__(self):
        super().__init__("This expense does not belong to your family.")


class InvalidCategoryForExpenseException(ValidationException):
    def __init__(self, category_id: str):
        super().__init__(
            f"Category '{category_id}' is not valid for this family or does not exist.",
        )


class InvalidCreditCardForExpenseException(ValidationException):
    def __init__(self, card_id: str):
        super().__init__(
            f"Credit card '{card_id}' is not valid for this family or does not exist.",
        )


class InstallmentMisconfigurationException(ValidationException):
    def __init__(self, message: str):
        super().__init__(message)


class EmailAlreadyRegisteredException(ConflictException):
    def __init__(self, email: str):
        super().__init__(f"A user with email '{email}' is already registered.")


#
# ─── Serialization Helpers ───────────────────────────────────────────────────
#

def build_error_response(code: str, message: str, details: dict | None = None) -> dict:
    """Standardized error payload matching the API contract."""
    payload: dict = {"success": False, "error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return payload


#
# ─── Global Handlers ─────────────────────────────────────────────────────────
#

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(exc.code, exc.message, exc.details),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    details = {}
    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"][1:])
        details[field] = error["msg"]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_error_response("ERR_VALIDATION", "Request validation failed.", details),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_response(
            "ERR_DATABASE",
            "A database error occurred. Please try again later.",
            {"detail": str(exc) if settings.ENVIRONMENT == "development" else None},
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_response("ERR_INTERNAL", "An unexpected error occurred. Please try again later."),
    )
