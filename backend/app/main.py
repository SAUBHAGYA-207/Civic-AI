from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from backend.app.config import settings
from backend.app.database.session import init_db
from backend.app.api.reports import router as reports_router
from backend.app.api.reviews import router as reviews_router
from backend.app.api.dashboard import router as dashboard_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("civicpulse")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    logger.info("Initializing CivicPulse database tables...")
    init_db()
    logger.info(f"Ollama host configured: {settings.OLLAMA_HOST}")
    logger.info(f"Models: Vision={settings.VISION_MODEL}, Text={settings.TEXT_MODEL}")
    yield
    logger.info("CivicPulse backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Privacy-conscious civic grievance & infrastructure triage platform powered by local Qwen models.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(reports_router)
app.include_router(reviews_router)
app.include_router(dashboard_router)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred. Please try again or check server logs."},
    )

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs",
        "guideline": "AI extracts evidence; deterministic Python rules recommend actions; authorized humans handle consequential decisions.",
    }
