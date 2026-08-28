"""
Application entrypoint: FastAPI app factory and router wiring.

Usage (from project root):
    uvicorn app.main:app --reload

This module configures logging, middleware, exception handlers and attempts to
include optional routers (storage, vectorization, ingestion, analysis) if they exist.
"""
from dotenv import load_dotenv
load_dotenv()

import importlib
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Config and infrastructure
from app.config import get_settings
from app.modules.infrastructure.logger import setup_logging, get_logger
from app.modules.infrastructure.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    register_exception_handlers,
)

settings = get_settings()
setup_logging(level=settings.log_level)
logger = get_logger(__name__)

app = FastAPI(title="it-gate-agent", version="0.1.0", debug=settings.debug)

# CORS: allow the React dev server (CRA default port 3000) to call this API.
# Registered first so it wraps all other middleware and handles preflight requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

register_exception_handlers(app)


@app.get("/health", tags=["health"])
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "env": settings.env})


@app.get("/", tags=["root"])
async def root() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "it-gate-agent", "env": settings.env})


def try_include_router(module_path: str, router_attr: str = "router") -> bool:
    try:
        mod = importlib.import_module(module_path)
    except Exception as exc:
        logger.debug("Optional module %s not available: %s", module_path, exc)
        return False

    router = getattr(mod, router_attr, None)
    if router is None:
        logger.warning("Module %s imported but has no '%s' attribute", module_path, router_attr)
        return False

    try:
        app.include_router(router)
        logger.info("Included router from %s", module_path)
        return True
    except Exception as exc:
        logger.exception("Failed to include router from %s: %s", module_path, exc)
        return False

# Auth router (always included, not optional)
try_include_router("app.modules.auth.routes")

try_include_router("app.modules.auth.messages_routes")

try_include_router("app.modules.auth.chat_routes")

optional_routers: List[str] = [
    "app.modules.storage.routes",
    "app.modules.vectorization.routes",
    "app.modules.ingestion.routes",
    "app.modules.analysis.routes",
    "app.modules.search.routes",
    "app.modules.reporting.routes",
    "app.modules.projects.routes",
    "app.modules.orchestrator.routes",
]

for mod_path in optional_routers:
    try_include_router(mod_path)


@app.on_event("startup")
async def on_startup():
    logger.info("Starting it-gate-agent app (env=%s debug=%s)", settings.env, settings.debug)


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down it-gate-agent app")
