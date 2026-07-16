"""
PROJECT THEMIS - Exception Handlers
Version: 5.0

This module sets up global exception handlers for the application.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ThemisException(Exception):
    """Base exception for PROJECT THEMIS."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code


class FrameProcessingError(ThemisException):
    """Error during frame processing."""
    pass


class ModelNotLoadedError(ThemisException):
    """AI model not loaded."""
    pass


class DatabaseError(ThemisException):
    """Database operation error."""
    pass


class ConfigurationError(ThemisException):
    """Configuration error."""
    pass


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers."""

    @app.exception_handler(ThemisException)
    async def themis_exception_handler(request: Request, exc: ThemisException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "type": type(exc).__name__,
                    "message": exc.message,
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "type": "InternalServerError",
                    "message": str(exc),
                },
            },
        )
