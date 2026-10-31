from datetime import datetime, timezone, timedelta
from backend.app.schemas.fused_evidence import FusedEvidence, EvidenceItem
from backend.app.schemas.image_evidence import ImageEvidence
from backend.app.schemas.text_evidence import TextEvidence
from backend.app.triage.priority_rules import triage_engine
from backend.app.triage.department_router import department_router

def test_triage_immediate_danger_live_wire():
    text_ev = TextEvidence(
        issue_category="streetlight",
        reported_location="Near Park Gate",
        reported_impacts=["Pedestrians screaming"],
        reported_duration="1 hour",
        reported_safety_concerns=["Live wire sparking on wet pavement"],
        missing_information=[],
    )
    fused_ev = FusedEvidence(
        issue_category="streetlight",
        evidence=[],
        conflicts=[],
        unknowns=[],
        requires_human_review=True,
        review_reasons=["High hazard"],
        data_sufficiency="sufficient",
    )

    decision = triage_engine.evaluate(
        fused_evidence=fused_ev,
        text_evidence=text_ev,
        image_evidence=None,
    )

    assert decision.recommended_pathway == "urgent_human_review"
    assert "CREDIBLE_DANGER_INDICATOR" in decision.reason_codes
    assert "live wire" in decision.decision_metadata["detected_danger_signals"]

def test_triage_critical_access_obstruction():
    text_ev = TextEvidence(
        issue_category="road_damage",
        reported_location="Hospital entrance road",
        reported_impacts=["Ambulance blocked and cannot enter"],
        reported_duration="3 hours",
        reported_safety_concerns=["Emergency access obstructed"],
        missing_information=[],
    )
    fused_ev = FusedEvidence(
        issue_category="road_damage",
        evidence=[],
        conflicts=[],
        unknowns=[],
        requires_human_review=True,
        review_reasons=[],
        data_sufficiency="sufficient",
    )

    decision = triage_engine.evaluate(
        fused_evidence=fused_ev,
        text_evidence=text_ev,
        image_evidence=None,
    )

    assert decision.recommended_pathway == "urgent_human_review"
    assert "CRITICAL_ACCESS_OBSTRUCTION" in decision.reason_codes

def test_triage_insufficient_evidence_clarification():
    text_ev = TextEvidence(
        issue_category="road_damage",
        reported_location=None,
        reported_impacts=[],
        reported_duration=None,
        reported_safety_concerns=[],
        missing_information=["No location provided"],
    )
    fused_ev = FusedEvidence(
        issue_category="road_damage",
        evidence=[],
        conflicts=[],
        unknowns=["Missing location"],
        requires_human_review=True,
        review_reasons=["Missing location"],
        data_sufficiency="insufficient",
    )

    decision = triage_engine.evaluate(
        fused_evidence=fused_ev,
        text_evidence=text_ev,
        image_evidence=None,
    )

    assert decision.recommended_pathway == "request_clarification"
    assert "INSUFFICIENT_EVIDENCE" in decision.reason_codes

def test_triage_routine_maintenance():
    text_ev = TextEvidence(
        issue_category="waste_management",
        reported_location="Corner bin, Street 4",
        reported_impacts=["Overflowing dry leaves and papers"],
        reported_duration="1 day",
        reported_safety_concerns=[],
        missing_information=[],
    )
    img_ev = ImageEvidence(
        issue_candidates=["waste_management"],
        visible_observations=["Public dustbin filled with paper waste"],
        visible_damage_characteristics=["Litter"],
        visible_obstruction_indicators=[],
        contextual_features=["Sidewalk"],
        image_quality="good",
        limitations_of_visual_assessment=[],
        not_visually_verifiable=[],
    )
    fused_ev = FusedEvidence(
        issue_category="waste_management",
        evidence=[],
        conflicts=[],
        unknowns=[],
        requires_human_review=False,
        review_reasons=[],
        data_sufficiency="sufficient",
    )

    decision = triage_engine.evaluate(
        fused_evidence=fused_ev,
        text_evidence=text_ev,
        image_evidence=img_ev,
    )

    assert decision.recommended_pathway == "standard_triage"
    assert "ROUTINE_MAINTENANCE_ELIGIBLE" in decision.reason_codes

def test_triage_waiting_time_escalation():
    text_ev = TextEvidence(
        issue_category="drainage",
        reported_location="Lane 3",
        reported_impacts=["Slow water runoff"],
        reported_duration=None,
        reported_safety_concerns=[],
        missing_information=[],
    )
    fused_ev = FusedEvidence(
        issue_category="drainage",
        evidence=[],
        conflicts=[],
        unknowns=[],
        requires_human_review=False,
        review_reasons=[],
        data_sufficiency="sufficient",
    )

    # Created 80 hours ago
    created_old = datetime.now(timezone.utc) - timedelta(hours=80)
    decision = triage_engine.evaluate(
        fused_evidence=fused_ev,
        text_evidence=text_ev,
        image_evidence=None,
        report_created_at=created_old,
    )

    assert decision.recommended_pathway == "urgent_human_review"
    assert "WAITING_TIME_ESCALATION_OVER_72H" in decision.reason_codes

def test_triage_reviewer_override():
    text_ev = TextEvidence(
        issue_category="waste_management",
        reported_location="Market square",
        reported_impacts=[],
        reported_duration=None,
        reported_safety_concerns=[],
        missing_information=[],
    )
    fused_ev = FusedEvidence(
        issue_category="waste_management",
        evidence=[],
        conflicts=[],
        unknowns=[],
        requires_human_review=False,
        review_reasons=[],
        data_sufficiency="sufficient",
    )

    decision = triage_engine.evaluate(
        fused_evidence=fused_ev,
        text_evidence=text_ev,
        reviewer_override="urgent_human_review",
        override_reason="VIP convoy route clearance inspection",
        override_actor="ward_officer_patna",
    )

    assert decision.recommended_pathway == "urgent_human_review"
    assert "HUMAN_REVIEWER_OVERRIDE" in decision.reason_codes
    assert decision.decision_metadata["override"]["reviewer_id"] == "ward_officer_patna"

def test_department_router():
    rec_road = department_router.route(category="road_damage", address_or_landmark="Boring Road, Patna")
    assert "Road Maintenance" in rec_road.department_name
    assert rec_road.department_status == "recommended"
    assert rec_road.is_official_referral is False

    rec_unknown = department_router.route(category="unknown")
    assert rec_unknown.department_status == "needs_verification"
    assert rec_unknown.is_official_referral is False
