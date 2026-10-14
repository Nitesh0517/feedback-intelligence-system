from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import logger
from app.core.errors import (
    AppBaseException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.api.v1.api import api_router
from app.api.v1.health import router as health_router
from app.db.session import SessionLocal
from app.services.user_service import seed_initial_admin


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds hardened production security headers to all HTTP responses."""
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    # Seed initial administrator if credentials configured in environment
    db = SessionLocal()
    try:
        seed_initial_admin(db)
    except Exception as exc:
        logger.warning(f"Initial administrator setup skipped or failed: {exc}")
    finally:
        db.close()

    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Hardened Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS Configuration
origins = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
if settings.ENVIRONMENT == "production" and "*" in origins:
    logger.warning("Wildcard CORS detected in production; removing wildcard for credential security.")
    origins = [o for o in origins if o != "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "Retry-After"],
)

# Centralized Error Handlers
app.add_exception_handler(AppBaseException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Health and Readiness probes (public)
app.include_router(health_router, tags=["Health"])

# Versioned API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "docs": f"{settings.API_V1_STR}/docs",
    }
