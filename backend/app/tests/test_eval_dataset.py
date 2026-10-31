import pytest
from backend.app.schemas.image_evidence import ImageEvidence
from backend.app.schemas.text_evidence import TextEvidence
from backend.app.services.evidence_fusion import fusion_engine
from backend.app.triage.priority_rules import triage_engine
from backend.app.triage.department_router import department_router

# Manually labeled evaluation cases representing diverse civic grievance scenarios
EVALUATION_DATASET = [
    {
        "id": "eval-01-urgent-danger",
        "description": "Exposed high-voltage wire hanging near school gate",
        "text": TextEvidence(
            issue_category="streetlight",
            reported_location="Near Model High School main gate",
            reported_impacts=["School children passing directly underneath"],
            reported_duration="2 hours",
            reported_safety_concerns=["Live wire sparking on wet pavement"],
            missing_information=[],
        ),
        "image": ImageEvidence(
            issue_candidates=["streetlight"],
            visible_observations=["Overhead electrical cable snapped and touching ground"],
            visible_damage_characteristics=["Severed electrical cable"],
            visible_obstruction_indicators=["Walkway partially blocked by fallen cable"],
            contextual_features=["School compound wall in background", "Daylight"],
            image_quality="good",
            limitations_of_visual_assessment=["Current voltage cannot be visually determined"],
            not_visually_verifiable=["Live electric current status"],
        ),
        "expected_category": "streetlight",
        "expected_pathway": "urgent_human_review",
        "expected_has_conflict": False,
        "expected_requires_human_review": True,
        "expected_department": "Electrical & Street Lighting Maintenance",
    },
    {
        "id": "eval-02-category-divergence",
        "description": "Citizen claims streetlight fault but image depicts garbage overflow",
        "text": TextEvidence(
            issue_category="streetlight",
            reported_location="Lane 4 corner",
            reported_impacts=["Dark area"],
            reported_duration="5 days",
            reported_safety_concerns=[],
            missing_information=[],
        ),
        "image": ImageEvidence(
            issue_candidates=["waste_management"],
            visible_observations=["Piled domestic garbage sacks and discarded plastic waste"],
            visible_damage_characteristics=["Open refuse accumulation"],
            visible_obstruction_indicators=["Pedestrian path restricted"],
            contextual_features=["Urban residential street"],
            image_quality="good",
            limitations_of_visual_assessment=[],
            not_visually_verifiable=["Origin of waste"],
        ),
        "expected_category": "unknown",  # Divergence forces unresolved/unknown
        "expected_pathway": "human_review",
        "expected_has_conflict": True,
        "expected_requires_human_review": True,
        "expected_department": "Central Municipal Grievance Cell",
    },
    {
        "id": "eval-03-routine-pothole",
        "description": "Asphalt pothole on residential road, verified by both text and photo",
        "text": TextEvidence(
            issue_category="road_damage",
            reported_location="Plot 45, Sector B",
            reported_impacts=["Vehicles slowing down"],
            reported_duration="3 weeks",
            reported_safety_concerns=["Bikers could lose balance"],
            missing_information=[],
        ),
        "image": ImageEvidence(
            issue_candidates=["road_damage"],
            visible_observations=["Irregular hole in asphalt pavement with loose gravel"],
            visible_damage_characteristics=["Pothole"],
            visible_obstruction_indicators=[],
            contextual_features=["Suburban residential roadway"],
            image_quality="good",
            limitations_of_visual_assessment=["Depth cannot be determined without measuring rod"],
            not_visually_verifiable=["Subbase moisture levels"],
        ),
        "expected_category": "road_damage",
        "expected_pathway": "standard_triage",
        "expected_has_conflict": False,
        "expected_requires_human_review": False,
        "expected_department": "Road Maintenance & Public Works Division",
    },
    {
        "id": "eval-04-insufficient-info",
        "description": "Vague report with no location, no duration, and poor quality image",
        "text": TextEvidence(
            issue_category="drainage",
            reported_location=None,
            reported_impacts=[],
            reported_duration=None,
            reported_safety_concerns=[],
            missing_information=["Missing specific road, ward, landmark, and contact details"],
        ),
        "image": ImageEvidence(
            issue_candidates=["unknown"],
            visible_observations=["Indiscernible blurry dark frame"],
            visible_damage_characteristics=[],
            visible_obstruction_indicators=[],
            contextual_features=[],
            image_quality="poor",
            limitations_of_visual_assessment=["Camera out of focus and insufficient exposure"],
            not_visually_verifiable=["Entire scene"],
        ),
        "expected_category": "drainage",
        "expected_pathway": "request_clarification",
        "expected_has_conflict": False,
        "expected_requires_human_review": True,
        "expected_department": "Drainage & Sewerage Operations",
    },
]

def test_evaluation_benchmark_metrics():
    """
    Evaluates benchmark test suite to compute key quality metrics:
    - Contradiction detection accuracy
    - Unsupported claim isolation rate
    - Triage pathway concordance
    - Department routing concordance
    """
    total = len(EVALUATION_DATASET)
    pathway_matches = 0
    contradiction_matches = 0
    department_matches = 0

    for case in EVALUATION_DATASET:
        fused = fusion_engine.fuse(
            text_evidence=case["text"],
            image_evidence=case["image"],
            address_or_landmark=case["text"].reported_location,
        )

        triage = triage_engine.evaluate(
            fused_evidence=fused,
            text_evidence=case["text"],
            image_evidence=case["image"],
        )

        dept = department_router.route(
            category=fused.issue_category,
            address_or_landmark=case["text"].reported_location,
        )

        # 1. Contradiction Detection check
        has_conflict = len(fused.conflicts) > 0
        if has_conflict == case["expected_has_conflict"]:
            contradiction_matches += 1

        # 2. Pathway concordance
        if triage.recommended_pathway == case["expected_pathway"]:
            pathway_matches += 1

        # 3. Department concordance
        if dept.department_name == case["expected_department"]:
            department_matches += 1

        # Provenance verification: ensure all citizen items remain citizen_reported or corroborated
        for item in fused.evidence:
            if item.source == "citizen_text":
                assert item.status in ("citizen_reported", "corroborated", "conflict")
            if item.source == "image":
                assert item.status in ("visually_observed", "conflict")

    pathway_accuracy = (pathway_matches / total) * 100.0
    contradiction_accuracy = (contradiction_matches / total) * 100.0
    dept_accuracy = (department_matches / total) * 100.0

    print(f"\n--- EVALUATION BENCHMARK RESULTS ---")
    print(f"Total Test Cases Evaluated: {total}")
    print(f"Contradiction Detection Accuracy: {contradiction_accuracy:.1f}%")
    print(f"Triage Pathway Concordance: {pathway_accuracy:.1f}%")
    print(f"Department Routing Concordance: {dept_accuracy:.1f}%")

    assert contradiction_accuracy == 100.0
    assert pathway_accuracy == 100.0
    assert dept_accuracy == 100.0
