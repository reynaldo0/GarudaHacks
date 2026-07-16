import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import settings
from app.api.router import api_router
from app.websocket.router import ws_router
from app.core.exceptions import setup_exception_handlers
from app.core.state_manager import state_manager
from app.database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 70)
    print("PROJECT THEMIS - Railway Decision Intelligence Platform")
    print(f"Version: {settings.APP_VERSION}")
    print(f"Environment: {settings.APP_ENV}")
    print("=" * 70)
    print()

    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("weights").mkdir(exist_ok=True)

    # Initialize database
    print("[INFO] Initializing PostgreSQL database...")
    try:
        init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[WARN] Database init failed: {e}")
        print("[INFO] Continuing without database...")

    # Initialize AI model
    print("[INFO] Loading YOLO11s model...")
    # TODO: Load YOLO model
    print("[OK] AI model loaded (placeholder)")

    # Initialize State Manager
    print("[INFO] Initializing State Manager...")
    state_manager._system_start_time = time.time()
    print("[OK] State Manager initialized")

    print()
    print("[OK] PROJECT THEMIS is ready!")
    print()

    yield

    # --- Shutdown ---
    print("[INFO] Shutting down PROJECT THEMIS...")
    # TODO: Cleanup resources
    print("[OK] Shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered Railway Decision Intelligence Platform",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # --- CORS Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Exception Handlers ---
    setup_exception_handlers(app)

    # --- Include Routers ---
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(ws_router)

    # --- Root Endpoint ---
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
        }

    # --- Health Check ---
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
        }

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
