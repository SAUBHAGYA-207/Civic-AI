from datetime import datetime, timezone, timedelta
from typing import Optional, Any
from backend.app.schemas.fused_evidence import FusedEvidence
from backend.app.schemas.image_evidence import ImageEvidence
from backend.app.schemas.text_evidence import TextEvidence
from backend.app.schemas.report import ReviewPathway, TriageDecisionSchema

RULE_VERSION = "v1.0.0"

# Dangerous keywords or indicators indicating credible immediate threat
IMMEDIATE_DANGER_KEYWORDS = {
    "live wire", "exposed wire", "electric shock", "sparking", "electrocution",
    "open manhole", "uncovered manhole", "deep ditch", "sinkhole", "road collapse",
    "gas leak", "chemical spill", "fire", "explosion", "flooding inside home",
    "school bus blocked", "ambulance blocked", "hospital entrance blocked"
}

OBSTRUCTION_KEYWORDS = {
    "blocked", "blockage", "impassable", "cannot pass", "access cut", "traffic jam",
    "completely submerged", "preventing movement", "trapped"
}

CRITICAL_ACCESS_KEYWORDS = {
    "hospital", "clinic", "school", "emergency", "ambulance", "arterial", "main highway"
}

class TriageEngine:
    """
    Deterministic rule-based triage engine implementing safety safeguards.
    Evaluates evidence records without relying on uncalibrated model scores.
    """
    version = RULE_VERSION

    def evaluate(
        self,
        fused_evidence: FusedEvidence,
        text_evidence: TextEvidence,
        image_evidence: Optional[ImageEvidence] = None,
        report_created_at: Optional[datetime] = None,
        reviewer_override: Optional[ReviewPathway] = None,
        override_reason: Optional[str] = None,
        override_actor: Optional[str] = None,
    ) -> TriageDecisionSchema:
        reason_codes: list[str] = []
        metadata: dict[str, Any] = {
            "eval_timestamp": datetime.now(timezone.utc).isoformat(),
            "rule_version": self.version,
        }

        # Handle Reviewer Override if present
        if reviewer_override:
            reason_codes.append("HUMAN_REVIEWER_OVERRIDE")
            metadata["override"] = {
                "reviewer_id": override_actor or "authorized_reviewer",
                "override_pathway": reviewer_override,
                "reason": override_reason or "Manual administrative override applied",
            }
            return TriageDecisionSchema(
                rule_version=self.version,
                recommended_pathway=reviewer_override,
                reason_codes=reason_codes,
                decision_metadata=metadata,
                created_at=datetime.now(timezone.utc).isoformat(),
            )

        # 1. Check for Credible Immediate Danger Indicators
        all_text_corpus = (
            " ".join(text_evidence.reported_safety_concerns) + " " +
            " ".join(text_evidence.reported_impacts) + " " +
            (text_evidence.reported_location or "")
        ).lower()

        visible_corpus = ""
        if image_evidence:
            visible_corpus = (
                " ".join(image_evidence.visible_observations) + " " +
                " ".join(image_evidence.visible_damage_characteristics) + " " +
                " ".join(image_evidence.visible_obstruction_indicators)
            ).lower()

        combined_corpus = f"{all_text_corpus} {visible_corpus}"

        detected_danger_signals = [
            kw for kw in IMMEDIATE_DANGER_KEYWORDS if kw in combined_corpus
        ]

        # 2. Check for Critical Access Impairment (e.g. hospital/school route)
        critical_access_signals = [
            kw for kw in CRITICAL_ACCESS_KEYWORDS if kw in combined_corpus
        ]
        obstruction_signals = [
            kw for kw in OBSTRUCTION_KEYWORDS if kw in combined_corpus
        ]

        is_urgent = False
        if detected_danger_signals:
            is_urgent = True
            reason_codes.append("CREDIBLE_DANGER_INDICATOR")
            metadata["detected_danger_signals"] = detected_danger_signals

        if critical_access_signals and obstruction_signals:
            is_urgent = True
            reason_codes.append("CRITICAL_ACCESS_OBSTRUCTION")
            metadata["critical_signals"] = critical_access_signals
            metadata["obstruction_signals"] = obstruction_signals

        if is_urgent:
            return TriageDecisionSchema(
                rule_version=self.version,
                recommended_pathway="urgent_human_review",
                reason_codes=reason_codes,
                decision_metadata=metadata,
                created_at=datetime.now(timezone.utc).isoformat(),
            )

        # 3. Check for Meaningful Conflicts or Ambiguities
        if fused_evidence.conflicts:
            reason_codes.append("EVIDENCE_CONFLICT_DETECTED")
            metadata["conflicts"] = fused_evidence.conflicts
            return TriageDecisionSchema(
                rule_version=self.version,
                recommended_pathway="human_review",
                reason_codes=reason_codes,
                decision_metadata=metadata,
                created_at=datetime.now(timezone.utc).isoformat(),
            )

        # 4. Check for Insufficient Evidence Requiring Clarification
        if fused_evidence.data_sufficiency == "insufficient":
            reason_codes.append("INSUFFICIENT_EVIDENCE")
            metadata["gaps"] = fused_evidence.unknowns
            return TriageDecisionSchema(
                rule_version=self.version,
                recommended_pathway="request_clarification",
                reason_codes=reason_codes,
                decision_metadata=metadata,
                created_at=datetime.now(timezone.utc).isoformat(),
            )

        # 5. Check Time Spent Waiting (Escalation)
        if report_created_at:
            # Ensure timezone awareness
            created_utc = report_created_at if report_created_at.tzinfo else report_created_at.replace(tzinfo=timezone.utc)
            waiting_time = datetime.now(timezone.utc) - created_utc
            if waiting_time > timedelta(hours=72):
                reason_codes.append("WAITING_TIME_ESCALATION_OVER_72H")
                metadata["waiting_hours"] = waiting_time.total_seconds() / 3600.0
                return TriageDecisionSchema(
                    rule_version=self.version,
                    recommended_pathway="urgent_human_review",
                    reason_codes=reason_codes,
                    decision_metadata=metadata,
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            elif waiting_time > timedelta(hours=24):
                reason_codes.append("WAITING_TIME_ESCALATION_OVER_24H")
                metadata["waiting_hours"] = waiting_time.total_seconds() / 3600.0
                return TriageDecisionSchema(
                    rule_version=self.version,
                    recommended_pathway="human_review",
                    reason_codes=reason_codes,
                    decision_metadata=metadata,
                    created_at=datetime.now(timezone.utc).isoformat(),
                )

        # 6. Poor image quality with claims
        if image_evidence and image_evidence.image_quality == "poor":
            reason_codes.append("POOR_IMAGE_QUALITY")
            return TriageDecisionSchema(
                rule_version=self.version,
                recommended_pathway="human_review",
                reason_codes=reason_codes,
                decision_metadata=metadata,
                created_at=datetime.now(timezone.utc).isoformat(),
            )

        # 7. Unresolved Category
        if fused_evidence.issue_category in ("unknown", "other"):
            reason_codes.append("UNRESOLVED_CATEGORY")
            return TriageDecisionSchema(
                rule_version=self.version,
                recommended_pathway="human_review",
                reason_codes=reason_codes,
                decision_metadata=metadata,
                created_at=datetime.now(timezone.utc).isoformat(),
            )

        # 8. Standard Triage (Routine verifiable complaint)
        reason_codes.append("ROUTINE_MAINTENANCE_ELIGIBLE")
        metadata["sufficiency"] = fused_evidence.data_sufficiency
        return TriageDecisionSchema(
            rule_version=self.version,
            recommended_pathway="standard_triage",
            reason_codes=reason_codes,
            decision_metadata=metadata,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

triage_engine = TriageEngine()
