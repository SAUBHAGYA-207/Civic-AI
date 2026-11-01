import os
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database.session import get_db
from backend.app.database.repository import ReportRepository
from backend.app.services.storage import storage_service
from backend.app.services.analysis_pipeline import analysis_pipeline
from backend.app.schemas.report import (
    ReportCreateResponse, ReportDetail, PaginatedReports, ReportSummaryItem,
    AttachmentRead, EvidenceRecordRead, TriageDecisionSchema, StatusHistoryRead,
    DepartmentRecommendation
)

router = APIRouter(prefix="/api/reports", tags=["reports"])

def serialize_report_detail(report) -> ReportDetail:
    attachments_read = [
        AttachmentRead(
            id=a.id,
            filename=a.original_filename,
            mime_type=a.mime_type,
            file_size=a.file_size,
            url=f"/api/reports/attachments/{a.id}",
            created_at=a.created_at.isoformat(),
        )
        for a in report.attachments
    ]

    evidence_record_read = None
    if report.evidence_records:
        rec = report.evidence_records[-1]  # most recent record
        evidence_record_read = EvidenceRecordRead(
            id=rec.id,
            image_evidence=rec.image_evidence_json,
            text_evidence=rec.text_evidence_json,
            fused_evidence=rec.fused_evidence_json,
            model_identifiers=rec.model_identifiers or {},
            schema_version=rec.schema_version,
            created_at=rec.created_at.isoformat(),
        )

    triage_decision_read = None
    if report.triage_decisions:
        td = report.triage_decisions[-1]
        triage_decision_read = TriageDecisionSchema(
            rule_version=td.rule_version,
            recommended_pathway=td.recommended_pathway,
            reason_codes=td.reason_codes or [],
            decision_metadata=td.decision_metadata or {},
            created_at=td.created_at.isoformat(),
        )

    status_history_read = [
        StatusHistoryRead(
            id=h.id,
            previous_status=h.previous_status,
            new_status=h.new_status,
            actor_type=h.actor_type,
            actor_id=h.actor_id,
            reason=h.reason,
            created_at=h.created_at.isoformat(),
        )
        for h in report.status_history
    ]

    dept_rec = None
    if report.department_recommendation:
        try:
            dept_rec = DepartmentRecommendation(**report.department_recommendation)
        except Exception:
            dept_rec = None

    return ReportDetail(
        id=report.id,
        complaint_text=report.complaint_text,
        issue_category=report.issue_category,
        latitude=report.latitude,
        longitude=report.longitude,
        address_or_landmark=report.address_or_landmark,
        workflow_status=report.workflow_status,
        review_pathway=report.review_pathway,
        department_recommendation=dept_rec,
        processing_status=report.processing_status,
        created_at=report.created_at.isoformat(),
        updated_at=report.updated_at.isoformat(),
        attachments=attachments_read,
        evidence_record=evidence_record_read,
        triage_decision=triage_decision_read,
        status_history=status_history_read,
    )

@router.post("", response_model=ReportCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    complaint_text: str = Form(..., min_length=5, max_length=4000),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    address_or_landmark: Optional[str] = Form(None),
    citizen_category: Optional[str] = Form(None),
    images: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    """
    Accepts citizen grievance submission with optional images and location data.
    Validates input coordinates, text boundaries, and file signatures.
    """
    # 1. Validate Coordinates if present
    if latitude is not None and not (-90.0 <= latitude <= 90.0):
        raise HTTPException(status_code=400, detail="Invalid latitude. Must be between -90 and 90.")
    if longitude is not None and not (-180.0 <= longitude <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid longitude. Must be between -180 and 180.")

    # 2. Clean category hint
    category_hint = citizen_category.strip().lower() if citizen_category else "unknown"
    if category_hint not in ("road_damage", "water_leakage", "drainage", "waste_management", "streetlight", "other", "unknown"):
        category_hint = "unknown"

    repo = ReportRepository(db)

    # 3. Create Report Record
    report = repo.create_report(
        complaint_text=complaint_text.strip(),
        issue_category=category_hint,
        latitude=latitude,
        longitude=longitude,
        address_or_landmark=address_or_landmark.strip() if address_or_landmark else None,
    )

    # 4. Process and store image attachments
    for img_file in images:
        if img_file.filename:
            storage_path, orig_name, mime_type, file_size = await storage_service.save_upload(img_file)
            repo.add_attachment(
                report_id=report.id,
                storage_path=storage_path,
                original_filename=orig_name,
                mime_type=mime_type,
                file_size=file_size,
            )

    return ReportCreateResponse(
        report_id=report.id,
        processing_status=report.processing_status,
        message="Grievance submitted successfully. Evidence extraction ready to run.",
        created_at=report.created_at.isoformat(),
    )

@router.post("/{report_id}/analyze", response_model=ReportDetail)
async def analyze_report(
    report_id: str,
    db: Session = Depends(get_db),
):
    """
    Executes multimodal evidence extraction, fusion, triage rules, and department recommendation.
    Guards against unintended duplicate execution if already completed.
    """
    repo = ReportRepository(db)
    report = repo.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Complaint report not found.")

    if report.processing_status == "processing":
        raise HTTPException(status_code=409, detail="Analysis is already in progress for this report.")

    updated_report = await analysis_pipeline.run(report_id=report_id, db=db)
    return serialize_report_detail(updated_report)

@router.get("/{report_id}", response_model=ReportDetail)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves full complaint report detail including evidence record and timeline."""
    repo = ReportRepository(db)
    report = repo.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Complaint report not found.")
    return serialize_report_detail(report)

@router.get("", response_model=PaginatedReports)
def list_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    pathway: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lists public/reviewer report summaries with pagination and filtering."""
    skip = (page - 1) * limit
    repo = ReportRepository(db)
    items, total = repo.list_reports(
        skip=skip,
        limit=limit,
        category=category,
        pathway=pathway,
        status=status,
    )

    summary_items = []
    for r in items:
        dept_name = None
        if r.department_recommendation:
            dept_name = r.department_recommendation.get("department_name")

        summary_items.append(
            ReportSummaryItem(
                id=r.id,
                created_at=r.created_at.isoformat(),
                issue_category=r.issue_category,
                address_or_landmark=r.address_or_landmark,
                workflow_status=r.workflow_status,
                review_pathway=r.review_pathway,
                department_name=dept_name,
                has_image=len(r.attachments) > 0,
                processing_status=r.processing_status,
            )
        )

    return PaginatedReports(
        total=total,
        page=page,
        limit=limit,
        items=summary_items,
    )

@router.get("/attachments/{attachment_id}")
def serve_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
):
    """Securely streams uploaded image attachments."""
    from backend.app.database.models import Attachment
    attachment = db.get(Attachment, attachment_id)
    if not attachment or not os.path.exists(attachment.storage_path):
        raise HTTPException(status_code=404, detail="Attachment not found.")

    return FileResponse(
        path=attachment.storage_path,
        media_type=attachment.mime_type,
        filename=attachment.original_filename,
    )
