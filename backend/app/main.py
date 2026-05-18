"""
TaskPilot AI — FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.utils.logger import configure_root_logger, get_logger
from app.middleware.auth_middleware import AuthMiddleware
from app.routes import auth, ai, calendar
from app.models.schemas import HealthResponse

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_root_logger(settings.log_level)
    logger.info({"action": "startup", "log_level": settings.log_level})
    yield
    logger.info({"action": "shutdown"})


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="TaskPilot AI",
        description="Voice-enabled Agentic AI assistant for task and meeting scheduling.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # ── Auth middleware ────────────────────────────────────────────────────────
    app.add_middleware(AuthMiddleware)

    # ── Global exception handler ───────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error({
            "action": "unhandled_exception",
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
        }, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred."},
        )

    # ── Request logging middleware ─────────────────────────────────────────────
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        response = await call_next(request)
        logger.info({
            "action": "http_request",
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
        })
        return response

    # ── Routers ────────────────────────────────────────────────────────────────
    app.include_router(auth.router)
    app.include_router(ai.router)
    app.include_router(calendar.router)

    # ── Health check ───────────────────────────────────────────────────────────
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health():
        return HealthResponse()

    return app


app = create_app()
