from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import logger


class AppBaseException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, error_code: str = "BAD_REQUEST", details: any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details


class NotFoundException(AppBaseException):
    """Resource not found exception."""
    def __init__(self, message: str = "Resource not found", details: any = None):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND, error_code="NOT_FOUND", details=details)


class ValidationException(AppBaseException):
    """Business validation exception."""
    def __init__(self, message: str, details: any = None):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, error_code="VALIDATION_ERROR", details=details)


class UnauthorizedException(AppBaseException):
    """Authentication required or invalid credentials exception."""
    def __init__(self, message: str = "Could not validate credentials", details: any = None):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED, error_code="UNAUTHORIZED", details=details)


class ForbiddenException(AppBaseException):
    """Insufficient permissions / role authorization exception."""
    def __init__(self, message: str = "Operation not permitted", details: any = None):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN, error_code="FORBIDDEN", details=details)


class ConflictException(AppBaseException):
    """Resource conflict exception (e.g. unique constraint collision)."""
    def __init__(self, message: str = "Resource conflict", details: any = None):
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT, error_code="CONFLICT", details=details)


class BadRequestException(AppBaseException):
    """General bad request exception."""
    def __init__(self, message: str = "Bad request", details: any = None):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST, error_code="BAD_REQUEST", details=details)



async def app_exception_handler(request: Request, exc: AppBaseException) -> JSONResponse:
    logger.warning(f"Handled application exception: {exc.message} (code: {exc.error_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "details": exc.details
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning(f"HTTP exception: {exc.detail} (status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "details": None
        }
    )


from fastapi.encoders import jsonable_encoder


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning(f"Request validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": "Input validation failed",
            "error_code": "UNPROCESSABLE_ENTITY",
            "details": jsonable_encoder(exc.errors())
        }
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled internal server error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected server error occurred. Please try again later.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "details": None
        }
    )
