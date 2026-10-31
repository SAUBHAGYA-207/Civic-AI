from typing import Literal
from pydantic import BaseModel, Field
from backend.app.schemas.image_evidence import IssueCategory

EvidenceSource = Literal[
    "image",
    "citizen_text",
    "location_metadata",
    "reviewer",
]

EvidenceStatus = Literal[
    "visually_observed",
    "citizen_reported",
    "corroborated",
    "conflict",
    "unknown",
    "reviewer_verified",
]

class EvidenceItem(BaseModel):
    field: str = Field(description="Name of the evidence attribute or topic")
    value: str = Field(description="Content of the observation or claim")
    source: EvidenceSource = Field(description="Originating source of the information")
    status: EvidenceStatus = Field(description="Verification and corroboration state")
    reviewer_id: str | None = Field(default=None, description="Identifier of human reviewer if verified")
    verified_at: str | None = Field(default=None, description="ISO timestamp if verified by a human")
    notes: str | None = Field(default=None, description="Contextual note or rationale")

class FusedEvidence(BaseModel):
    issue_category: IssueCategory = Field(
        description="Synthesized issue category based on corroborated or candidate evidence"
    )
    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="List of all atomic evidence items with preserved provenance"
    )
    conflicts: list[str] = Field(
        default_factory=list,
        description="Meaningful contradictions detected between image observations and citizen claims"
    )
    unknowns: list[str] = Field(
        default_factory=list,
        description="Attributes that cannot be resolved from available evidence"
    )
    corroborations: list[str] = Field(
        default_factory=list,
        description="Points where visible evidence and citizen claims align"
    )
    requires_human_review: bool = Field(
        default=True,
        description="Flag indicating if ambiguity, conflict, or high risk mandates human attention"
    )
    review_reasons: list[str] = Field(
        default_factory=list,
        description="Specific reasons triggering mandatory human review"
    )
    data_sufficiency: Literal["sufficient", "partial", "insufficient"] = Field(
        default="partial",
        description="Administrative evaluation of whether enough facts exist to take action"
    )
