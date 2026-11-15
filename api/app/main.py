from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import Settings, settings
from app.core.errors import (
    AppError,
    app_error_handler,
    http_exception_handler,
    integrity_error_handler,
    validation_error_handler,
)
from app.core.logging import setup_logging
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.courses import router as courses_router
from app.routers.enrollments import router as enrollments_router
from app.routers.health import router as health_router
from app.routers.reviews import router as reviews_router
from app.routers.users import router as users_router


def create_app(config: Settings = settings) -> FastAPI:
    """Kreira i konfigurira FastAPI aplikaciju."""

    setup_logging(debug=config.ENV == "dev")
    app = FastAPI(title=config.APP_NAME, debug=config.ENV == "dev")

    app.add_exception_handler(AppError, app_error_handler)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # pyright: ignore[reportArgumentType]

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(courses_router)
    app.include_router(enrollments_router)
    app.include_router(categories_router)
    app.include_router(reviews_router)
    return app


app = create_app()
