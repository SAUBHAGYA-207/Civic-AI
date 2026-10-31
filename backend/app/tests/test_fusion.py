import pytest
from backend.app.schemas.image_evidence import ImageEvidence
from backend.app.schemas.text_evidence import TextEvidence
from backend.app.services.evidence_fusion import fusion_engine

def test_fusion_agreement_and_corroboration():
    text_ev = TextEvidence(
        issue_category="road_damage",
        reported_location="Main Street, opposite Post Office",
        reported_impacts=["Vehicles forced to brake sharply"],
        reported_duration="2 weeks",
        reported_safety_concerns=["Accident risk"],
        missing_information=[],
    )
    img_ev = ImageEvidence(
        issue_candidates=["road_damage"],
        visible_observations=["Asphalt crater visible in middle of lane"],
        visible_damage_characteristics=["Pothole"],
        visible_obstruction_indicators=["Lane partially blocked"],
        contextual_features=["Daylight road"],
        image_quality="good",
        limitations_of_visual_assessment=[],
        not_visually_verifiable=["Depth"],
    )

    fused = fusion_engine.fuse(
        text_evidence=text_ev,
        image_evidence=img_ev,
        latitude=25.5941,
        longitude=85.1376,
        address_or_landmark="Main Street, Patna",
    )

    assert fused.issue_category == "road_damage"
    assert len(fused.conflicts) == 0
    assert len(fused.corroborations) > 0
    assert any("substantiate issue category" in c for c in fused.corroborations)
    assert fused.data_sufficiency == "sufficient"

def test_fusion_text_only_no_image():
    text_ev = TextEvidence(
        issue_category="water_leakage",
        reported_location="Sector 4 park corner",
        reported_impacts=["Drinking water wasting"],
        reported_duration="4 hours",
        reported_safety_concerns=[],
        missing_information=[],
    )

    fused = fusion_engine.fuse(
        text_evidence=text_ev,
        image_evidence=None,
        latitude=None,
        longitude=None,
        address_or_landmark="Sector 4 park corner",
    )

    assert fused.issue_category == "water_leakage"
    assert any("lacks photographic evidence" in r for r in fused.review_reasons)
    assert fused.requires_human_review is True

def test_fusion_contradictory_categories():
    text_ev = TextEvidence(
        issue_category="streetlight",
        reported_location="7th Cross Road",
        reported_impacts=["Dark street at night"],
        reported_duration="1 month",
        reported_safety_concerns=["Theft risk"],
        missing_information=[],
    )
    img_ev = ImageEvidence(
        issue_candidates=["waste_management"],
        visible_observations=["Large heap of decomposing garbage on sidewalk"],
        visible_damage_characteristics=["Solid waste"],
        visible_obstruction_indicators=["Sidewalk blocked"],
        contextual_features=[],
        image_quality="good",
        limitations_of_visual_assessment=[],
        not_visually_verifiable=[],
    )

    fused = fusion_engine.fuse(
        text_evidence=text_ev,
        image_evidence=img_ev,
        latitude=25.6,
        longitude=85.1,
        address_or_landmark="7th Cross Road",
    )

    assert len(fused.conflicts) > 0
    assert any("Category divergence" in c for c in fused.conflicts)
    assert fused.requires_human_review is True

def test_fusion_poor_image_quality():
    text_ev = TextEvidence(
        issue_category="drainage",
        reported_location="Ward 12",
        reported_impacts=["Waterlogging"],
        reported_duration=None,
        reported_safety_concerns=[],
        missing_information=[],
    )
    img_ev = ImageEvidence(
        issue_candidates=["unknown"],
        visible_observations=["Extremely dark and blurry image"],
        visible_damage_characteristics=[],
        visible_obstruction_indicators=[],
        contextual_features=[],
        image_quality="poor",
        limitations_of_visual_assessment=["Lighting too dim to resolve details"],
        not_visually_verifiable=["Entire scene"],
    )

    fused = fusion_engine.fuse(
        text_evidence=text_ev,
        image_evidence=img_ev,
        latitude=25.6,
        longitude=85.1,
        address_or_landmark="Ward 12",
    )

    assert any("Poor image quality" in r for r in fused.review_reasons)
    assert fused.requires_human_review is True

def test_fusion_insufficient_location():
    text_ev = TextEvidence(
        issue_category="road_damage",
        reported_location=None,
        reported_impacts=[],
        reported_duration=None,
        reported_safety_concerns=[],
        missing_information=["Missing specific road name and city area"],
    )

    fused = fusion_engine.fuse(
        text_evidence=text_ev,
        image_evidence=None,
        latitude=None,
        longitude=None,
        address_or_landmark=None,
    )

    assert fused.data_sufficiency == "insufficient"
    assert any("Missing actionable location information" in r for r in fused.review_reasons)
