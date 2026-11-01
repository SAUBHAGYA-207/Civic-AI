from typing import Literal, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.schemas.image_evidence import IssueCategory, ImageEvidence
from backend.app.schemas.text_evidence import TextEvidence
from backend.app.schemas.fused_evidence import FusedEvidence

ReviewPathway = Literal[
    "urgent_human_review",
    "human_review",
    "request_clarification",
    "standard_triage",
]

WorkflowStatus = Literal[
    "submitted",
    "under_analysis",
    "awaiting_review",
    "in_progress",
    "resolved",
    "rejected",
    "clarification_requested",
]

ProcessingStatus = Literal[
    "pending",
    "processing",
    "completed",
    "failed",
]

DepartmentStatus = Literal[
    "recommended",
    "needs_verification",
]

class DepartmentRecommendation(BaseModel):
    department_name: str
    department_status: DepartmentStatus
    jurisdiction_level: str = "Municipal / Local"
    rationale: str
    is_official_referral: bool = Field(
        default=False,
        description="Must always be False unless an authenticated official webhook has acknowledged receipt"
    )

class TriageDecisionSchema(BaseModel):
    rule_version: str
    recommended_pathway: ReviewPathway
    reason_codes: list[str]
    decision_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None

class ReportCreateResponse(BaseModel):
    report_id: str
    processing_status: ProcessingStatus
    message: str
    created_at: str

class ReportStatusUpdate(BaseModel):
    new_status: WorkflowStatus
    actor_type: Literal["reviewer", "system", "citizen"] = "reviewer"
    actor_id: str = Field(min_length=2, max_length=100)
    reason: str = Field(min_length=5, max_length=500)

class AttachmentRead(BaseModel):
    id: str
    filename: str
    mime_type: str
    file_size: int
    url: str
    created_at: str

class StatusHistoryRead(BaseModel):
    id: str
    previous_status: str | None
    new_status: str
    actor_type: str
    actor_id: str
    reason: str
    created_at: str

class EvidenceRecordRead(BaseModel):
    id: str
    image_evidence: Optional[Any] = None
    text_evidence: Optional[Any] = None
    fused_evidence: Optional[Any] = None
    model_identifiers: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = "1.0.0"
    created_at: str

class ReportDetail(BaseModel):
    id: str
    complaint_text: str
    issue_category: IssueCategory
    latitude: float | None
    longitude: float | None
    address_or_landmark: str | None
    workflow_status: WorkflowStatus
    review_pathway: ReviewPathway | None
    department_recommendation: DepartmentRecommendation | None
    processing_status: ProcessingStatus
    created_at: str
    updated_at: str
    attachments: list[AttachmentRead] = Field(default_factory=list)
    evidence_record: EvidenceRecordRead | None = None
    triage_decision: TriageDecisionSchema | None = None
    status_history: list[StatusHistoryRead] = Field(default_factory=list)

class ReportSummaryItem(BaseModel):
    id: str
    created_at: str
    issue_category: IssueCategory
    address_or_landmark: str | None
    workflow_status: WorkflowStatus
    review_pathway: ReviewPathway | None
    department_name: str | None
    has_image: bool
    processing_status: ProcessingStatus

class PaginatedReports(BaseModel):
    total: int
    page: int
    limit: int
    items: list[ReportSummaryItem]

class DashboardSummary(BaseModel):
    total_reports: int
    reports_awaiting_review: int
    reports_urgent_review: int
    reports_in_progress: int
    reports_resolved: int
    reports_clarification_requested: int
    reports_overdue: int
    category_distribution: dict[str, int]
    pathway_distribution: dict[str, int]
    avg_response_time_hours: float | None
    median_response_time_hours: float | None

class HotspotItem(BaseModel):
    area_or_cluster: str
    count: int
    primary_category: IssueCategory
    latitude: float | None
    longitude: float | None
