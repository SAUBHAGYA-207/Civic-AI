from typing import Literal
from pydantic import BaseModel, Field

IssueCategory = Literal[
    "road_damage",
    "water_leakage",
    "drainage",
    "waste_management",
    "streetlight",
    "other",
    "unknown",
]

class ImageEvidence(BaseModel):
    issue_candidates: list[IssueCategory] = Field(
        default_factory=lambda: ["unknown"],
        description="Possible categories supported by visible evidence"
    )
    visible_observations: list[str] = Field(
        default_factory=list,
        description="Factual visual observations evident in the image"
    )
    visible_damage_characteristics: list[str] = Field(
        default_factory=list,
        description="Specific visible damage features such as pothole, exposed pipe, water ponding, garbage heap"
    )
    visible_obstruction_indicators: list[str] = Field(
        default_factory=list,
        description="Visible physical blockage of road, walkway, drain, or public path"
    )
    contextual_features: list[str] = Field(
        default_factory=list,
        description="Visible surrounding context such as residential area, road intersection, night/day"
    )
    image_quality: Literal["poor", "adequate", "good", "unknown"] = Field(
        default="unknown",
        description="Assessment of image resolution, clarity, lighting, and focus"
    )
    limitations_of_visual_assessment: list[str] = Field(
        default_factory=list,
        description="Inherent constraints such as angle, occlusion, lack of scale"
    )
    not_visually_verifiable: list[str] = Field(
        default_factory=list,
        description="Attributes that cannot be confirmed from the photograph alone"
    )
    extraction_error: str | None = Field(
        default=None,
        description="Error details if vision model extraction encountered issues"
    )
