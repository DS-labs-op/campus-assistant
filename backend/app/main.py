"""
Campus Assistant Chatbot - Main Application
A multilingual chatbot for educational institutions.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.core.config import get_settings
from app.core.database import init_db
from app.api import (
    chat_router,
    faq_router,
    document_router,
    admin_router,
    telegram_router,
)

settings = get_settings()

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
)

# Only add file logging if LOG_FILE is specified and not empty
if settings.log_file and settings.log_file.strip():
    try:
        import os
        log_dir = os.path.dirname(settings.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        logger.add(
            settings.log_file,
            rotation="1 day",
            retention="30 days",
            level=settings.log_level,
        )
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## Campus Assistant Chatbot

A multilingual conversational AI assistant for educational institutions.

### Features:
- **Multilingual Support**: Hindi, English, Gujarati, Marathi, Punjabi, Tamil, and more
- **FAQ Management**: Easy-to-manage FAQ database
- **Document Processing**: Upload and index PDFs, DOCX files
- **Context Awareness**: Multi-turn conversation support
- **Platform Integration**: Web, Telegram, WhatsApp

### API Groups:
- **/chat**: Main chatbot interaction endpoints
- **/faqs**: FAQ management (CRUD operations)
- **/documents**: Document upload and indexing
- **/admin**: Dashboard and analytics
- **/telegram**: Telegram bot integration
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(faq_router, prefix="/api/v1")
app.include_router(document_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(telegram_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/admin/health",
    }


# Health check (convenient shortcut)
@app.get("/health")
async def health():
    """Quick health check."""
    return {"status": "healthy", "version": settings.app_version}
