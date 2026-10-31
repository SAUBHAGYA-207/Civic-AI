import pytest
from pydantic import ValidationError
from backend.app.schemas.image_evidence import ImageEvidence
from backend.app.schemas.text_evidence import TextEvidence
from backend.app.schemas.fused_evidence import FusedEvidence, EvidenceItem
from backend.app.schemas.report import DepartmentRecommendation, TriageDecisionSchema

def test_image_evidence_valid():
    data = {
        "issue_candidates": ["road_damage"],
        "visible_observations": ["Large crater in asphalt", "Vehicular traffic swerving"],
        "visible_damage_characteristics": ["Pothole approximately 1 meter across"],
        "visible_obstruction_indicators": ["Lane partially blocked"],
        "contextual_features": ["Urban road during daylight"],
        "image_quality": "good",
        "limitations_of_visual_assessment": ["Depth cannot be confirmed without calibrated scale"],
        "not_visually_verifiable": ["Structural integrity of road base"],
    }
    evidence = ImageEvidence.model_validate(data)
    assert evidence.issue_candidates == ["road_damage"]
    assert evidence.image_quality == "good"
    assert len(evidence.visible_observations) == 2

def test_image_evidence_invalid_enum():
    with pytest.raises(ValidationError):
        ImageEvidence.model_validate({
            "issue_candidates": ["flying_cars"],  # Invalid category
            "visible_observations": [],
            "image_quality": "excellent",  # Invalid quality enum
        })

def test_text_evidence_valid():
    data = {
        "issue_category": "drainage",
        "reported_location": "Corner of 5th Ave and Oak St",
        "reported_impacts": ["Foul smell", "Water entering storefronts"],
        "reported_duration": "3 days",
        "reported_safety_concerns": ["Disease vector risk"],
        "missing_information": ["Exact drain inlet number"],
    }
    evidence = TextEvidence.model_validate(data)
    assert evidence.issue_category == "drainage"
    assert evidence.reported_location == "Corner of 5th Ave and Oak St"
    assert len(evidence.reported_impacts) == 2

def test_evidence_item_provenance():
    item = EvidenceItem(
        field="pothole_depth",
        value="Alleged 2 feet deep",
        source="citizen_text",
        status="citizen_reported",
    )
    assert item.source == "citizen_text"
    assert item.status == "citizen_reported"

    # Test invalid provenance source
    with pytest.raises(ValidationError):
        EvidenceItem(
            field="test",
            value="test",
            source="external_api",  # Not allowed
            status="visually_observed",
        )

def test_fused_evidence_schema():
    item = EvidenceItem(
        field="road_crack",
        value="Visible fissure",
        source="image",
        status="visually_observed"
    )
    fused = FusedEvidence(
        issue_category="road_damage",
        evidence=[item],
        conflicts=[],
        unknowns=["Duration"],
        corroborations=[],
        requires_human_review=False,
        review_reasons=[],
        data_sufficiency="sufficient",
    )
    assert fused.issue_category == "road_damage"
    assert len(fused.evidence) == 1
    assert fused.data_sufficiency == "sufficient"
