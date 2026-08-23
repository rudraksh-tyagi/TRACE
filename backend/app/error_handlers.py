"""
TRACE global FastAPI error handlers.
"""

import logging

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.exceptions import TraceException


logger = logging.getLogger(
    "trace.error_handler"
)


def register_error_handlers(
    app: FastAPI,
) -> None:
    """
    Register all global TRACE exception handlers.
    """

    # ========================================================
    # TRACE APPLICATION ERRORS
    # ========================================================

    @app.exception_handler(TraceException)
    async def trace_exception_handler(
        request: Request,
        exc: TraceException,
    ) -> JSONResponse:

        logger.warning(
            "TRACE error | method=%s | path=%s | "
            "code=%s | message=%s",
            request.method,
            request.url.path,
            exc.error_code,
            exc.message,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "path": request.url.path,
            },
        )

    # ========================================================
    # FASTAPI REQUEST VALIDATION
    # ========================================================

    @app.exception_handler(
        RequestValidationError
    )
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:

        logger.warning(
            "Request validation failed | "
            "method=%s | path=%s | errors=%s",
            request.method,
            request.url.path,
            exc.errors(),
        )

        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "error_code": "VALIDATION_ERROR",
                "message": (
                    "The request payload failed "
                    "schema validation."
                ),
                "path": request.url.path,
                "details": exc.errors(),
            },
        )

    # ========================================================
    # PYDANTIC VALIDATION
    # ========================================================

    @app.exception_handler(
        ValidationError
    )
    async def pydantic_validation_handler(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:

        logger.error(
            "Pydantic validation error | "
            "path=%s | errors=%s",
            request.url.path,
            exc.errors(),
        )

        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "error_code": "PYDANTIC_VALIDATION_ERROR",
                "message": (
                    "Pipeline data failed "
                    "Pydantic validation."
                ),
                "path": request.url.path,
                "details": exc.errors(),
            },
        )

    # ========================================================
    # KEY ERRORS
    # ========================================================

    @app.exception_handler(KeyError)
    async def key_error_handler(
        request: Request,
        exc: KeyError,
    ) -> JSONResponse:

        logger.error(
            "Missing required data field | "
            "path=%s | key=%s",
            request.url.path,
            exc,
        )

        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error_code": "MISSING_DATA_FIELD",
                "message": (
                    f"Required data field is missing: {exc}"
                ),
                "path": request.url.path,
            },
        )

    # ========================================================
    # UNEXPECTED ERRORS
    # ========================================================

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:

        logger.exception(
            "Unhandled server error | "
            "method=%s | path=%s",
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": (
                    "An unexpected internal error occurred."
                ),
                "path": request.url.path,
            },
        )