from typing import Optional
from backend.app.schemas.image_evidence import ImageEvidence, IssueCategory
from backend.app.schemas.text_evidence import TextEvidence
from backend.app.schemas.fused_evidence import (
    FusedEvidence, EvidenceItem, EvidenceSource, EvidenceStatus
)

CATEGORY_SYNONYMS = {
    "road_damage": {"road", "pothole", "asphalt", "cracks", "pavement", "street", "highway", "traffic"},
    "water_leakage": {"water", "pipe", "leak", "pipeline", "gushing", "drinking water", "tap"},
    "drainage": {"drain", "gutter", "sewage", "overflow", "stagnant water", "manhole", "nallah"},
    "waste_management": {"garbage", "trash", "waste", "debris", "dump", "litter", "rubbish"},
    "streetlight": {"light", "lamp", "pole", "dark", "bulb", "illumination", "wire"},
}

class EvidenceFusionEngine:
    """
    Deterministic Python fusion engine.
    Combines image visual observations, citizen claims, and location metadata into
    a single structured record while rigorously maintaining provenance and verification statuses.
    """

    def fuse(
        self,
        text_evidence: TextEvidence,
        image_evidence: Optional[ImageEvidence],
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        address_or_landmark: Optional[str] = None,
        citizen_selected_category: Optional[IssueCategory] = None,
    ) -> FusedEvidence:
        evidence_items: list[EvidenceItem] = []
        conflicts: list[str] = []
        unknowns: list[str] = []
        corroborations: list[str] = []
        review_reasons: list[str] = []

        # 1. Evaluate Location Information
        has_coords = (latitude is not None and longitude is not None)
        has_address = bool(address_or_landmark and address_or_landmark.strip())
        reported_loc_text = text_evidence.reported_location

        if has_coords:
            evidence_items.append(
                EvidenceItem(
                    field="device_coordinates",
                    value=f"{latitude}, {longitude}",
                    source="location_metadata",
                    status="visually_observed" if image_evidence and image_evidence.image_quality != "poor" else "citizen_reported",
                    notes="GPS coordinates recorded at submission",
                )
            )
        if has_address:
            evidence_items.append(
                EvidenceItem(
                    field="address_or_landmark",
                    value=address_or_landmark.strip(),
                    source="location_metadata",
                    status="citizen_reported",
                    notes="Explicit address or landmark supplied by user",
                )
            )
        if reported_loc_text:
            evidence_items.append(
                EvidenceItem(
                    field="text_reported_location",
                    value=reported_loc_text.strip(),
                    source="citizen_text",
                    status="citizen_reported",
                    notes="Location mentioned inside complaint narrative",
                )
            )

        if not has_coords and not has_address and not reported_loc_text:
            unknowns.append("No geographic coordinates, address, or landmark provided")
            review_reasons.append("Missing actionable location information")

        # 2. Text Claims
        for impact in text_evidence.reported_impacts:
            evidence_items.append(
                EvidenceItem(
                    field="reported_impact",
                    value=impact,
                    source="citizen_text",
                    status="citizen_reported",
                )
            )

        if text_evidence.reported_duration:
            evidence_items.append(
                EvidenceItem(
                    field="reported_duration",
                    value=text_evidence.reported_duration,
                    source="citizen_text",
                    status="citizen_reported",
                )
            )
        else:
            unknowns.append("Duration of the issue is unspecified in complaint text")

        for concern in text_evidence.reported_safety_concerns:
            evidence_items.append(
                EvidenceItem(
                    field="reported_safety_concern",
                    value=concern,
                    source="citizen_text",
                    status="citizen_reported",
                )
            )

        for missing in text_evidence.missing_information:
            unknowns.append(f"Text claim gap: {missing}")

        # 3. Image Observations (if present)
        text_cat = text_evidence.issue_category
        resolved_category: IssueCategory = text_cat

        if image_evidence:
            # Check Image Quality
            if image_evidence.image_quality == "poor":
                unknowns.append("Image quality is poor (insufficient clarity, lighting, or resolution)")
                review_reasons.append("Poor image quality hampers visual verification")

            # Visible observations
            for obs in image_evidence.visible_observations:
                evidence_items.append(
                    EvidenceItem(
                        field="visible_observation",
                        value=obs,
                        source="image",
                        status="visually_observed",
                    )
                )

            for dmg in image_evidence.visible_damage_characteristics:
                evidence_items.append(
                    EvidenceItem(
                        field="visible_damage",
                        value=dmg,
                        source="image",
                        status="visually_observed",
                    )
                )

            for obs_ind in image_evidence.visible_obstruction_indicators:
                evidence_items.append(
                    EvidenceItem(
                        field="visible_obstruction",
                        value=obs_ind,
                        source="image",
                        status="visually_observed",
                    )
                )

            for ctx in image_evidence.contextual_features:
                evidence_items.append(
                    EvidenceItem(
                        field="contextual_feature",
                        value=ctx,
                        source="image",
                        status="visually_observed",
                    )
                )

            for lim in image_evidence.limitations_of_visual_assessment:
                unknowns.append(f"Visual limitation: {lim}")

            for unv in image_evidence.not_visually_verifiable:
                unknowns.append(f"Not visually verifiable: {unv}")

            # 4. Category Comparison & Corroboration / Conflict Analysis
            image_candidates = set(image_evidence.issue_candidates)
            all_text_words = (
                text_cat + " " + " ".join(text_evidence.reported_impacts) + " " + " ".join(text_evidence.reported_safety_concerns)
            ).lower()

            # Check if image candidates contain text category
            if text_cat in image_candidates and text_cat not in ("unknown", "other"):
                resolved_category = text_cat
                corroborations.append(f"Both photograph and complaint text substantiate issue category: {text_cat}")
                # Corroborated category evidence item
                evidence_items.append(
                    EvidenceItem(
                        field="corroborated_category",
                        value=text_cat,
                        source="citizen_text",
                        status="corroborated",
                        notes="Image evidence candidates directly include citizen reported category",
                    )
                )
            elif "unknown" in image_candidates and len(image_candidates) == 1:
                # Image did not conclusively identify category
                if text_cat != "unknown":
                    resolved_category = text_cat
                    unknowns.append("Visual evidence did not independently identify a distinct category")
                else:
                    resolved_category = citizen_selected_category or "unknown"
            elif text_cat not in image_candidates and text_cat != "unknown" and "unknown" not in image_candidates:
                # Potential category divergence
                conflict_desc = (
                    f"Category divergence: Citizen text indicates '{text_cat}', while image analysis suggests "
                    f"{list(image_candidates)}. This may reflect different facets of the situation or unrelated media."
                )
                conflicts.append(conflict_desc)
                review_reasons.append(conflict_desc)
                evidence_items.append(
                    EvidenceItem(
                        field="category_divergence",
                        value=f"Text: {text_cat} vs Image: {list(image_candidates)}",
                        source="image",
                        status="conflict",
                        notes="Discrepancy between visible evidence candidates and claimed category",
                    )
                )
                resolved_category = "unknown"
            else:
                # Fallback to candidate or citizen hint
                if image_candidates and "unknown" not in image_candidates:
                    resolved_category = list(image_candidates)[0]
                else:
                    resolved_category = text_cat if text_cat != "unknown" else (citizen_selected_category or "unknown")

            # Check for obstruction corroboration
            if image_evidence.visible_obstruction_indicators and any(
                "block" in w or "obstruction" in w or "access" in w for w in text_evidence.reported_impacts
            ):
                corroborations.append("Physical path or roadway obstruction reported by citizen is visibly observed in image")

        else:
            # No image attached
            unknowns.append("No photograph provided with report; claims remain uncorroborated by visual evidence")
            review_reasons.append("Report lacks photographic evidence")
            resolved_category = text_cat if text_cat != "unknown" else (citizen_selected_category or "unknown")

        # 5. Determine Data Sufficiency
        has_actionable_location = (has_coords or has_address or reported_loc_text)
        has_identifiable_category = (resolved_category != "unknown")
        has_sufficient_visuals = (image_evidence is not None and image_evidence.image_quality != "poor")

        if has_actionable_location and has_identifiable_category and has_sufficient_visuals:
            data_sufficiency = "sufficient"
        elif has_actionable_location and (has_identifiable_category or has_sufficient_visuals):
            data_sufficiency = "partial"
        else:
            data_sufficiency = "insufficient"

        # 6. Check if Human Review is Mandatory
        requires_human_review = (
            len(conflicts) > 0
            or len(review_reasons) > 0
            or resolved_category in ("unknown", "other")
            or data_sufficiency == "insufficient"
            or (image_evidence is not None and image_evidence.image_quality == "poor")
        )

        return FusedEvidence(
            issue_category=resolved_category,
            evidence=evidence_items,
            conflicts=conflicts,
            unknowns=unknowns,
            corroborations=corroborations,
            requires_human_review=requires_human_review,
            review_reasons=review_reasons,
            data_sufficiency=data_sufficiency,
        )

fusion_engine = EvidenceFusionEngine()
