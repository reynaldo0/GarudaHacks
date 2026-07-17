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
from app.ai.spatial_engine import SpatialEngine
from app.ai.occupancy_engine import OccupancyEngine
from app.ai.lookup_table import LookupTable
from app.ai.fusion_engine import FusionEngine
from app.ai.ccales_engine import CCALESEngine
from app.ai.decision_engine import DecisionEngine
from app.ai.redistribution_engine import RedistributionEngine
from app.ai.door_engine import DoorEngine
from app.ai.announcement_engine import AnnouncementEngine

# Global AI engine instances
spatial_engine = None
occupancy_engine = None
lookup_table = None
fusion_engine = None
cales_engine = None
decision_engine = None
redistribution_engine = None
door_engine = None
announcement_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # --- Startup ---
    print("=" * 70)
    print("PROJECT THEMIS - Railway Decision Intelligence Platform")
    print(f"Version: {settings.APP_VERSION}")
    print(f"Environment: {settings.APP_ENV}")
    print("=" * 70)
    print()

    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("weights").mkdir(exist_ok=True)
    Path(settings.FISHEYE_CALIBRATION_DIR).mkdir(parents=True, exist_ok=True)

    # Initialize database
    print("[INFO] Initializing PostgreSQL database...")
    try:
        init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[WARN] Database init failed: {e}")
        print("[INFO] Continuing without database...")

    # Initialize AI engines
    global spatial_engine, occupancy_engine, lookup_table, fusion_engine
    global cales_engine, decision_engine, redistribution_engine
    global door_engine, announcement_engine

    print("[INFO] Initializing AI engines...")
    spatial_engine = SpatialEngine()
    occupancy_engine = OccupancyEngine()
    lookup_table = LookupTable()
    fusion_engine = FusionEngine()
    cales_engine = CCALESEngine()
    decision_engine = DecisionEngine()
    redistribution_engine = RedistributionEngine()
    door_engine = DoorEngine()
    announcement_engine = AnnouncementEngine()
    print("[OK] AI engines initialized (spatial, occupancy, lookup, fusion, cales, decision, redistribution, door, announcement)")

    print("[INFO] Loading Spatial Occupancy Segmentation model...")
    spatial_loaded = spatial_engine.load()
    if spatial_loaded:
        print("[OK] Spatial segmentation model loaded")
    else:
        print("[WARN] Spatial segmentation model not loaded (weights not found)")

    # Initialize State Manager
    print("[INFO] Initializing State Manager...")
    state_manager._system_start_time = time.time()
    print("[OK] State Manager initialized")

    # Auto-seed default scenario
    print("[INFO] Seeding default occupancy data...")
    from app.simulation.seeder import seed_default
    try:
        await seed_default()
        print("[OK] Default scenario seeded")
    except Exception as e:
        print(f"[WARN] Seeding failed: {e}")

    # Wire WebSocket manager to Integration Hub
    from app.websocket.router import manager as ws_manager
    from app.core.integration_hub import integration_hub
    integration_hub.set_websocket_manager(ws_manager)
    print("[OK] WebSocket manager wired to Integration Hub")

    print()
    print("[OK] PROJECT THEMIS V6 is ready!")
    print()

    yield

    # --- Shutdown ---
    print("[INFO] Shutting down PROJECT THEMIS...")
    try:
        from app.database.connection import engine
        engine.dispose()
        print("[OK] Database connections closed")
    except Exception as e:
        print(f"[WARN] Database cleanup error: {e}")
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
        allow_origins=settings.cors_origins_list,
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
