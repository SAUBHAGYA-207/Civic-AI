from datetime import datetime, timezone, timedelta
from typing import Optional, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, select

from backend.app.database.models import (
    Report, Attachment, EvidenceRecord, TriageDecision, StatusHistory, utc_now
)
from backend.app.schemas.report import (
    ReviewPathway, WorkflowStatus, ProcessingStatus
)

class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_report(
        self,
        complaint_text: str,
        issue_category: str = "unknown",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        address_or_landmark: Optional[str] = None,
    ) -> Report:
        report = Report(
            complaint_text=complaint_text,
            issue_category=issue_category,
            latitude=latitude,
            longitude=longitude,
            address_or_landmark=address_or_landmark,
            workflow_status="submitted",
            processing_status="pending",
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        # Initial status history record
        history = StatusHistory(
            report_id=report.id,
            previous_status=None,
            new_status="submitted",
            actor_type="system",
            actor_id="civicpulse_system",
            reason="Complaint registered by citizen",
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(report)
        return report

    def add_attachment(
        self,
        report_id: str,
        storage_path: str,
        original_filename: str,
        mime_type: str,
        file_size: int,
    ) -> Attachment:
        attachment = Attachment(
            report_id=report_id,
            storage_path=storage_path,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
        )
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def get_report(self, report_id: str) -> Optional[Report]:
        stmt = (
            select(Report)
            .where(Report.id == report_id)
            .options(
                joinedload(Report.attachments),
                joinedload(Report.evidence_records),
                joinedload(Report.triage_decisions),
                joinedload(Report.status_history),
            )
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def list_reports(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        pathway: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[Report], int]:
        query = select(Report).options(joinedload(Report.attachments))

        if category and category != "all":
            query = query.where(Report.issue_category == category)
        if pathway and pathway != "all":
            query = query.where(Report.review_pathway == pathway)
        if status and status != "all":
            query = query.where(Report.workflow_status == status)

        # Count total
        count_query = select(func.count(Report.id))
        if category and category != "all":
            count_query = count_query.where(Report.issue_category == category)
        if pathway and pathway != "all":
            count_query = count_query.where(Report.review_pathway == pathway)
        if status and status != "all":
            count_query = count_query.where(Report.workflow_status == status)

        total = self.db.scalar(count_query) or 0
        items = self.db.execute(
            query.order_by(desc(Report.created_at)).offset(skip).limit(limit)
        ).unique().scalars().all()

        return list(items), total

    def update_processing_status(self, report_id: str, status: ProcessingStatus) -> None:
        report = self.db.get(Report, report_id)
        if report:
            report.processing_status = status
            report.updated_at = utc_now()
            self.db.commit()

    def save_analysis_results(
        self,
        report_id: str,
        issue_category: str,
        review_pathway: str,
        department_rec: dict[str, Any],
        image_evidence: Optional[dict[str, Any]],
        text_evidence: Optional[dict[str, Any]],
        fused_evidence: Optional[dict[str, Any]],
        model_identifiers: dict[str, Any],
        rule_version: str,
        reason_codes: list[str],
        decision_metadata: dict[str, Any],
    ) -> Report:
        report = self.db.get(Report, report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        report.issue_category = issue_category
        report.review_pathway = review_pathway
        report.department_recommendation = department_rec
        report.processing_status = "completed"
        
        # Determine appropriate workflow status after analysis
        if report.workflow_status == "submitted" or report.workflow_status == "under_analysis":
            if review_pathway == "request_clarification":
                report.workflow_status = "clarification_requested"
            else:
                report.workflow_status = "awaiting_review"

        report.updated_at = utc_now()

        # Evidence Record
        record = EvidenceRecord(
            report_id=report.id,
            image_evidence_json=image_evidence,
            text_evidence_json=text_evidence,
            fused_evidence_json=fused_evidence,
            model_identifiers=model_identifiers,
            schema_version="1.0.0",
        )
        self.db.add(record)

        # Triage Decision
        triage = TriageDecision(
            report_id=report.id,
            rule_version=rule_version,
            recommended_pathway=review_pathway,
            reason_codes=reason_codes,
            decision_metadata=decision_metadata,
        )
        self.db.add(triage)

        self.db.commit()
        self.db.refresh(report)
        return report

    def update_status(
        self,
        report_id: str,
        new_status: str,
        actor_type: str,
        actor_id: str,
        reason: str,
    ) -> Report:
        report = self.db.get(Report, report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        prev_status = report.workflow_status
        report.workflow_status = new_status
        report.updated_at = utc_now()

        history = StatusHistory(
            report_id=report.id,
            previous_status=prev_status,
            new_status=new_status,
            actor_type=actor_type,
            actor_id=actor_id,
            reason=reason,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_dashboard_summary(self) -> dict[str, Any]:
        # Live queries
        total = self.db.scalar(select(func.count(Report.id))) or 0
        awaiting = self.db.scalar(
            select(func.count(Report.id)).where(Report.workflow_status == "awaiting_review")
        ) or 0
        urgent = self.db.scalar(
            select(func.count(Report.id)).where(
                Report.review_pathway == "urgent_human_review",
                Report.workflow_status.in_(["awaiting_review", "under_analysis", "submitted"])
            )
        ) or 0
        in_progress = self.db.scalar(
            select(func.count(Report.id)).where(Report.workflow_status == "in_progress")
        ) or 0
        resolved = self.db.scalar(
            select(func.count(Report.id)).where(Report.workflow_status == "resolved")
        ) or 0
        clarification = self.db.scalar(
            select(func.count(Report.id)).where(Report.workflow_status == "clarification_requested")
        ) or 0

        # Overdue reports: pending or awaiting review created more than 48 hours ago
        cutoff_48h = utc_now() - timedelta(hours=48)
        overdue = self.db.scalar(
            select(func.count(Report.id)).where(
                Report.workflow_status.in_(["submitted", "awaiting_review"]),
                Report.created_at < cutoff_48h
            )
        ) or 0

        # Category distribution
        cat_rows = self.db.execute(
            select(Report.issue_category, func.count(Report.id)).group_by(Report.issue_category)
        ).all()
        category_distribution = {cat: count for cat, count in cat_rows if cat}

        # Pathway distribution
        path_rows = self.db.execute(
            select(Report.review_pathway, func.count(Report.id)).group_by(Report.review_pathway)
        ).all()
        pathway_distribution = {p: count for p, count in path_rows if p}

        # Response time metrics (time between created_at and first resolved/in_progress transition)
        history_resolved = self.db.execute(
            select(StatusHistory.report_id, func.min(StatusHistory.created_at))
            .where(StatusHistory.new_status.in_(["resolved", "in_progress"]))
            .group_by(StatusHistory.report_id)
        ).all()

        response_hours: list[float] = []
        for rep_id, first_action_time in history_resolved:
            rep = self.db.get(Report, rep_id)
            if rep and rep.created_at and first_action_time:
                # Ensure timezone awareness compatibility
                c_at = rep.created_at if rep.created_at.tzinfo else rep.created_at.replace(tzinfo=timezone.utc)
                a_at = first_action_time if first_action_time.tzinfo else first_action_time.replace(tzinfo=timezone.utc)
                diff = (a_at - c_at).total_seconds() / 3600.0
                if diff >= 0:
                    response_hours.append(diff)

        avg_time = round(sum(response_hours) / len(response_hours), 2) if response_hours else None
        median_time = None
        if response_hours:
            sorted_hrs = sorted(response_hours)
            mid = len(sorted_hrs) // 2
            median_time = round(sorted_hrs[mid] if len(sorted_hrs) % 2 != 0 else (sorted_hrs[mid - 1] + sorted_hrs[mid]) / 2.0, 2)

        return {
            "total_reports": total,
            "reports_awaiting_review": awaiting,
            "reports_urgent_review": urgent,
            "reports_in_progress": in_progress,
            "reports_resolved": resolved,
            "reports_clarification_requested": clarification,
            "reports_overdue": overdue,
            "category_distribution": category_distribution,
            "pathway_distribution": pathway_distribution,
            "avg_response_time_hours": avg_time,
            "median_response_time_hours": median_time,
        }

    def get_hotspots(self) -> list[dict[str, Any]]:
        # Group geographically rounded coordinates or landmarks to preserve citizen privacy
        reports_with_geo = self.db.execute(
            select(
                func.round(Report.latitude, 2).label("lat_approx"),
                func.round(Report.longitude, 2).label("lon_approx"),
                Report.address_or_landmark,
                Report.issue_category,
                func.count(Report.id).label("count")
            )
            .where(Report.latitude.isnot(None), Report.longitude.isnot(None))
            .group_by("lat_approx", "lon_approx", Report.issue_category)
            .order_by(desc("count"))
            .limit(50)
        ).all()

        hotspots = []
        for r in reports_with_geo:
            area_name = r.address_or_landmark or f"Coordinates ({r.lat_approx}, {r.lon_approx})"
            hotspots.append({
                "area_or_cluster": area_name,
                "count": r.count,
                "primary_category": r.issue_category,
                "latitude": float(r.lat_approx) if r.lat_approx is not None else None,
                "longitude": float(r.lon_approx) if r.lon_approx is not None else None,
            })
        return hotspots
