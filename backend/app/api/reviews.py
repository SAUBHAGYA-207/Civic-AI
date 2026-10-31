from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database.session import get_db
from backend.app.database.repository import ReportRepository
from backend.app.schemas.report import ReportStatusUpdate, ReportDetail, WorkflowStatus
from backend.app.api.reports import serialize_report_detail

router = APIRouter(prefix="/api/reports", tags=["reviews"])

VALID_TRANSITIONS: dict[str, set[str]] = {
    "submitted": {"under_analysis", "awaiting_review", "clarification_requested", "rejected"},
    "under_analysis": {"awaiting_review", "clarification_requested", "rejected"},
    "awaiting_review": {"in_progress", "clarification_requested", "resolved", "rejected"},
    "in_progress": {"resolved", "clarification_requested", "rejected", "awaiting_review"},
    "clarification_requested": {"awaiting_review", "in_progress", "rejected"},
    "resolved": {"in_progress", "awaiting_review"},  # re-opened cases
    "rejected": {"awaiting_review"},  # appeal review
}

def verify_reviewer_auth(x_reviewer_token: Optional[str] = Header(None)) -> str:
    """Verifies that the reviewer possesses the configured administrative key."""
    if not x_reviewer_token or x_reviewer_token != settings.REVIEWER_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. A valid reviewer secret token is required to perform status updates."
        )
    return x_reviewer_token

@router.post("/{report_id}/updates", response_model=ReportDetail)
def update_report_status(
    report_id: str,
    update_data: ReportStatusUpdate,
    db: Session = Depends(get_db),
    auth_token: str = Depends(verify_reviewer_auth),
):
    """
    Authorized endpoint for municipal case workers and reviewers to transition complaint states.
    Validates state transition logic, records identity, timestamp, and audit justification.
    """
    repo = ReportRepository(db)
    report = repo.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Complaint report not found.")

    current_status = report.workflow_status
    target_status = update_data.new_status

    if current_status == target_status:
        raise HTTPException(
            status_code=400,
            detail=f"Report is already in '{target_status}' status."
        )

    allowed = VALID_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state transition from '{current_status}' to '{target_status}'. Allowed target statuses: {sorted(list(allowed))}"
        )

    updated_report = repo.update_status(
        report_id=report.id,
        new_status=target_status,
        actor_type=update_data.actor_type,
        actor_id=update_data.actor_id,
        reason=update_data.reason,
    )

    return serialize_report_detail(updated_report)
