from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.database.repository import ReportRepository
from backend.app.services.ollama_client import ollama_client
from backend.app.schemas.report import DashboardSummary, HotspotItem

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Computes real-time, database-derived metrics including status counts,
    priority pathway distributions, overdue tracking, and response-time averages.
    """
    repo = ReportRepository(db)
    summary_data = repo.get_dashboard_summary()
    return DashboardSummary(**summary_data)

@router.get("/hotspots", response_model=list[HotspotItem])
def get_dashboard_hotspots(db: Session = Depends(get_db)):
    """
    Retrieves geographically aggregated complaints clustered by rounded coordinates
    or localized landmarks, preserving individual privacy.
    """
    repo = ReportRepository(db)
    hotspots = repo.get_hotspots()
    return [HotspotItem(**h) for h in hotspots]

@router.get("/health")
def get_system_health():
    """Returns local inference runtime, model readiness, and service status."""
    ollama_health = ollama_client.check_health()
    return {
        "service": "CivicPulse AI Backend",
        "status": "operational" if ollama_health.get("status") == "healthy" else "degraded",
        "ollama": ollama_health,
    }
