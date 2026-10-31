from typing import Literal
from pydantic import BaseModel, Field
from backend.app.schemas.image_evidence import IssueCategory

class TextEvidence(BaseModel):
    issue_category: IssueCategory = Field(
        default="unknown",
        description="The primary issue category claimed in the citizen complaint"
    )
    reported_location: str | None = Field(
        default=None,
        description="Location, street, landmark, or area claimed in the text"
    )
    reported_impacts: list[str] = Field(
        default_factory=list,
        description="Reported impacts on residents, traffic, public health, or access"
    )
    reported_duration: str | None = Field(
        default=None,
        description="How long the issue has persisted according to citizen text"
    )
    reported_safety_concerns: list[str] = Field(
        default_factory=list,
        description="Any specific hazards or safety risks alleged by the citizen"
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="Key information missing from the text complaint (e.g. specific spot, duration)"
    )
    extraction_error: str | None = Field(
        default=None,
        description="Error details if text claim extraction encountered issues"
    )
