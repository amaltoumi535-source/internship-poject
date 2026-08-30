# app/modules/infrastructure/middleware.py
"""
Middleware for request tracking, logging, and exception handling.
"""

import uuid
from datetime import datetime
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.modules.infrastructure.logger import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request for tracing."""

    async def dispatch(self, request: Request, call_next: Callable):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests and outgoing responses."""

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = getattr(request.state, "request_id", "unknown")
        start_time = datetime.utcnow()
        
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )

        response = await call_next(request)
        
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)",
            extra={"request_id": request_id, "status_code": response.status_code},
        )

        return response


def register_exception_handlers(app):
    """Register global exception handlers."""

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception(
            f"[{request_id}] Unhandled exception",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            f"[{request_id}] Validation error: {str(exc)}",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "request_id": request_id,
            },
        )
