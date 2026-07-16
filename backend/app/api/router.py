"""
PROJECT THEMIS - API Router
Version: 5.0

This module aggregates all API routers.
"""

from fastapi import APIRouter

from app.api.endpoints import health, frame, occupancy, state, history, config, simulation

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(frame.router, tags=["Frame"])
api_router.include_router(occupancy.router, tags=["Occupancy"])
api_router.include_router(state.router, tags=["State"])
api_router.include_router(history.router, tags=["History"])
api_router.include_router(config.router, tags=["Configuration"])
api_router.include_router(simulation.router, tags=["Simulation"])
