"""
FastAPI middleware utilities:
- RequestIDMiddleware: attach a request id (X-Request-ID)
- LoggingMiddleware: log basic request/response info
- register_exception_handlers(app): register handler that converts BaseAppException -> JSONResponse
"""

import time
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import FastAPI
from .exceptions import BaseAppException
from .logger import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Add an X-Request-ID header (and request.state.request_id) to each request.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response: Response = await call_next(request)
        # ensure header in response
        response.headers.setdefault("X-Request-ID", request_id)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Log start/end of requests with duration and status code.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.time()
        try:
            logger.info("started request", extra={"method": request.method, "path": request.url.path})
            response: Response = await call_next(request)
            duration_ms = int((time.time() - start) * 1000)
            logger.info(
                "completed request",
                extra={"method": request.method, "path": request.url.path, "status_code": response.status_code, "duration_ms": duration_ms}
            )
            return response
        except Exception as exc:
            duration_ms = int((time.time() - start) * 1000)
            logger.exception("unhandled exception in request", exc_info=exc)
            # Re-raise; let registered exception handlers format this
            raise


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register handler for BaseAppException to convert to JSONResponse.
    Call this during app startup after creating FastAPI app.
    """
    @app.exception_handler(BaseAppException)
    async def base_app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        payload = exc.to_dict() if hasattr(exc, "to_dict") else {"detail": str(exc)}
        return JSONResponse(status_code=exc.status_code, content=payload)