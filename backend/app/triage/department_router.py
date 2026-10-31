from backend.app.schemas.image_evidence import IssueCategory
from backend.app.schemas.report import DepartmentRecommendation, DepartmentStatus

DEPARTMENT_MAPPINGS: dict[str, dict[str, str]] = {
    "road_damage": {
        "name": "Road Maintenance & Public Works Division",
        "rationale": "Potholes, surface cracks, asphalt degradation, and street paving issues fall under municipal road infrastructure.",
    },
    "water_leakage": {
        "name": "Water Supply & Pipeline Distribution",
        "rationale": "Potable water pipeline breaches, leaking mains, and valve failures require water utility maintenance.",
    },
    "drainage": {
        "name": "Drainage & Sewerage Operations",
        "rationale": "Open drains, overflowing gutters, stormwater blockage, and sewage backups are handled by sanitation engineering.",
    },
    "waste_management": {
        "name": "Municipal Solid Waste Management",
        "rationale": "Accumulated garbage, open dumping, and uncleared waste bins fall under solid waste sanitation squads.",
    },
    "streetlight": {
        "name": "Electrical & Street Lighting Maintenance",
        "rationale": "Non-functional streetlights, damaged lamp poles, and exposed street wiring require municipal electrical servicing.",
    },
}

class DepartmentRouter:
    """
    Deterministic department router suggesting responsible municipal departments.
    Explicitly distinguishes recommendation from official notification.
    """

    def route(
        self,
        category: IssueCategory,
        address_or_landmark: str | None = None,
        has_verified_jurisdiction: bool = False,
    ) -> DepartmentRecommendation:
        if category in DEPARTMENT_MAPPINGS and category not in ("other", "unknown"):
            mapping = DEPARTMENT_MAPPINGS[category]
            status: DepartmentStatus = "recommended" if has_verified_jurisdiction or address_or_landmark else "needs_verification"
            return DepartmentRecommendation(
                department_name=mapping["name"],
                department_status=status,
                jurisdiction_level="Urban Local Body / Municipal Corporation",
                rationale=mapping["rationale"],
                is_official_referral=False,
            )

        # Unclear or ambiguous category
        return DepartmentRecommendation(
            department_name="Central Municipal Grievance Cell",
            department_status="needs_verification",
            jurisdiction_level="Municipal Central Desk",
            rationale="Specific jurisdiction or issue category is unverified; central triage must assign department upon manual intake.",
            is_official_referral=False,
        )

department_router = DepartmentRouter()
