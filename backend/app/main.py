from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from loguru import logger
from app.core.logging import setup_logging
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from app.core.middleware import SecurityHeadersMiddleware
from app.api.v1.expenses import router as expenses_router
from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.credit_cards import router as credit_cards_router
from app.api.v1.debts import router as debts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.debug(f"Environment: {settings.ENVIRONMENT}")
    logger.debug(f"Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(SecurityHeadersMiddleware)

    application.add_exception_handler(AppException, app_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    application.add_exception_handler(Exception, generic_exception_handler)

    application.include_router(auth_router, prefix="/api/v1")
    application.include_router(expenses_router, prefix="/api/v1")
    application.include_router(categories_router, prefix="/api/v1")
    application.include_router(credit_cards_router, prefix="/api/v1")
    application.include_router(debts_router, prefix="/api/v1")

    @application.get("/health", tags=["Health"])
    async def health_check():
        logger.debug("Health check requested")
        return {"status": "ok", "version": settings.VERSION}

    logger.info(f"Routes registered: {len(application.routes)}")
    return application


app = create_application()
