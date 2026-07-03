import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.core.config import settings
from src.api.routes import chat_routes, session_routes, document_routes, auth_routes
from src.models.schemas import HealthResponse
from fastapi.responses import RedirectResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("zyntra.main")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="A production-ready multi-agent AI powered by Google ADK with file-based persistence.",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(chat_routes.router)
app.include_router(session_routes.router)
app.include_router(document_routes.router)

# Serve static files (frontend)
static_dir = Path(__file__).parent / "src" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Static files mounted from {static_dir}")

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Zyntra AI is running",
        "version": "1.0.0",
    }


@app.get("/api/v1/info", tags=["Info"])
async def get_info():
    """Get application information."""
    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "debug": settings.DEBUG,
        "persistence": "file-based",
    }


if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info("Persistence: File-based (data/ folder)")

    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.RELOAD,
    )