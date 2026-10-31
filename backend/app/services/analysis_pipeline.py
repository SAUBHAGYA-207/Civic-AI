import logging
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database.repository import ReportRepository
from backend.app.database.models import Report
from backend.app.schemas.image_evidence import ImageEvidence
from backend.app.schemas.text_evidence import TextEvidence
from backend.app.schemas.fused_evidence import FusedEvidence
from backend.app.services.image_extractor import image_extractor
from backend.app.services.text_extractor import text_extractor
from backend.app.services.evidence_fusion import fusion_engine
from backend.app.triage.priority_rules import triage_engine
from backend.app.triage.department_router import department_router

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    """
    Coordinates end-to-end evidence extraction, fusion, triage, and department recommendation.
    Enforces sequential model execution to prevent CPU/memory exhaustion.
    """

    async def run(
        self,
        report_id: str,
        db: Session,
    ) -> Report:
        repo = ReportRepository(db)
        report = repo.get_report(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        # Mark as processing
        repo.update_processing_status(report_id, "processing")

        try:
            # 1. Text Evidence Extraction (sequential stage 1)
            text_evidence, text_duration = await text_extractor.extract(report.complaint_text)

            # 2. Image Evidence Extraction (sequential stage 2 if attachment exists)
            image_evidence: Optional[ImageEvidence] = None
            image_duration = 0.0
            if report.attachments:
                # Analyze the first primary attachment
                primary_attachment = report.attachments[0]
                image_evidence, image_duration = await image_extractor.extract(
                    image_path=primary_attachment.storage_path,
                    complaint_context=report.complaint_text,
                )

            # 3. Evidence Fusion (deterministic Python stage 3)
            fused_evidence: FusedEvidence = fusion_engine.fuse(
                text_evidence=text_evidence,
                image_evidence=image_evidence,
                latitude=report.latitude,
                longitude=report.longitude,
                address_or_landmark=report.address_or_landmark,
                citizen_selected_category=report.issue_category if report.issue_category != "unknown" else None,
            )

            # 4. Triage Decision (deterministic Python rules stage 4)
            triage_decision = triage_engine.evaluate(
                fused_evidence=fused_evidence,
                text_evidence=text_evidence,
                image_evidence=image_evidence,
                report_created_at=report.created_at,
            )

            # 5. Department Recommendation (deterministic routing stage 5)
            dept_rec = department_router.route(
                category=fused_evidence.issue_category,
                address_or_landmark=report.address_or_landmark,
                has_verified_jurisdiction=bool(report.latitude and report.longitude),
            )

            # Model identifiers and performance tracking
            model_identifiers = {
                "vision_model": settings.VISION_MODEL if image_evidence else "none",
                "text_model": settings.TEXT_MODEL,
                "text_extraction_duration_sec": text_duration,
                "image_extraction_duration_sec": image_duration,
            }

            # 6. Persist to Database
            updated_report = repo.save_analysis_results(
                report_id=report.id,
                issue_category=fused_evidence.issue_category,
                review_pathway=triage_decision.recommended_pathway,
                department_rec=dept_rec.model_dump(),
                image_evidence=image_evidence.model_dump() if image_evidence else None,
                text_evidence=text_evidence.model_dump(),
                fused_evidence=fused_evidence.model_dump(),
                model_identifiers=model_identifiers,
                rule_version=triage_decision.rule_version,
                reason_codes=triage_decision.reason_codes,
                decision_metadata=triage_decision.decision_metadata,
            )

            return updated_report

        except Exception as e:
            logger.error(f"Analysis pipeline failed for report {report_id}: {e}", exc_info=True)
            repo.update_processing_status(report_id, "failed")
            raise

analysis_pipeline = AnalysisPipeline()
