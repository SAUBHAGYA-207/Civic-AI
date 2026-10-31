import logging
from backend.app.config import settings
from backend.app.schemas.text_evidence import TextEvidence
from backend.app.services.ollama_client import ollama_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a civic grievance claim extraction assistant.
Your task is to extract citizen claims, reported impacts, duration, alleged safety concerns, and missing details from citizen complaints.

CRITICAL OPERATIONAL RULES:
1. Extract CLAIMS, NOT VERIFIED FACTS. What the citizen writes is their report/allegation, not confirmed ground truth.
2. Categorize the claimed issue into one of:
   - road_damage
   - water_leakage
   - drainage
   - waste_management
   - streetlight
   - other
   - unknown
3. Identify reported locations, durations, impacts, and safety hazards mentioned in the text.
4. Identify MISSING INFORMATION that would normally be required for municipal action (e.g. missing precise landmark, missing duration, missing details on whether water is potable or sewage).
5. Do NOT embellish or infer facts not stated in the complaint text.

Respond strictly with a JSON object adhering to the specified schema."""

class TextClaimExtractor:
    def __init__(self):
        self.model = settings.TEXT_MODEL

    async def extract(
        self,
        complaint_text: str,
    ) -> tuple[TextEvidence, float]:
        """
        Extracts structured claims from citizen complaint text using Qwen2.5.
        Returns: (TextEvidence, duration_seconds)
        """
        schema = TextEvidence.model_json_schema()
        user_prompt = f"Extract all citizen claims and missing details from this complaint text:\n\n\"\"\"\n{complaint_text.strip()}\n\"\"\""

        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]

            parsed_json, duration = await ollama_client.chat_with_model(
                model=self.model,
                messages=messages,
                format_schema=schema,
                temperature=0.0,
            )

            evidence = TextEvidence.model_validate(parsed_json)
            return evidence, duration

        except Exception as e:
            logger.error(f"Text claim extraction failed: {e}")
            fallback = TextEvidence(
                issue_category="unknown",
                reported_location=None,
                reported_impacts=[],
                reported_duration=None,
                reported_safety_concerns=[],
                missing_information=["Automated text extraction was incomplete or encountered an error"],
                extraction_error=str(e),
            )
            return fallback, 0.0

text_extractor = TextClaimExtractor()
