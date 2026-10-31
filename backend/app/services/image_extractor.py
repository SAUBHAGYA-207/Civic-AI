import base64
import logging
from pathlib import Path
from PIL import Image
import io
from backend.app.config import settings
from backend.app.schemas.image_evidence import ImageEvidence
from backend.app.services.ollama_client import ollama_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a rigorous, objective civil infrastructure visual evidence analyst.
Your sole job is to document VISIBLE PHYSICAL EVIDENCE from photographs submitted with public infrastructure complaints.

ABSOLUTE OPERATIONAL CONSTRAINTS:
1. NEVER invent measurements, depths, widths, weights, or dimensions. Do not guess '5 feet deep' or '2 meters wide' without calibrated physical markers.
2. NEVER claim an accident or injury occurred unless physical vehicular wreckage or active emergency personnel are directly visible in the frame.
3. NEVER declare a road, bridge, drain, or structure 'structurally safe' or 'structurally unsafe' from a photo alone; visual assessment cannot determine internal structural integrity.
4. DO NOT treat citizen claims as visually confirmed facts. Citizen statements are external context, not ground truth.
5. NEVER claim that hidden, subterranean, or occluded conditions have been verified.
6. Report image quality objectively: 'poor' (blurry, dark, low res, out of focus), 'adequate' (acceptable visibility), 'good' (sharp, well-lit, clear view).
7. If damage is not clearly visible, record category as 'unknown' or 'other'.

Supported issue categories:
- road_damage
- water_leakage
- drainage
- waste_management
- streetlight
- other
- unknown

Respond strictly with a JSON object adhering to the specified schema."""

def preprocess_image_to_base64(image_path: str, max_dimension: int = 1024) -> str:
    """Preprocess image to ensure reasonable resolution for local VLM (saving memory/CPU)."""
    with Image.open(image_path) as img:
        # Convert to RGB if needed (e.g. RGBA or palette)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        
        # Resize if exceeding max_dimension
        width, height = img.size
        if max(width, height) > max_dimension:
            scale = max_dimension / max(width, height)
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

class ImageEvidenceExtractor:
    def __init__(self):
        self.model = settings.VISION_MODEL

    async def extract(
        self,
        image_path: str,
        complaint_context: str | None = None,
    ) -> tuple[ImageEvidence, float]:
        """
        Extracts structured visual evidence from an image using Qwen2.5-VL.
        Returns: (ImageEvidence, duration_seconds)
        """
        prompt_text = "Analyze this infrastructure photograph. Extract visible physical observations, damage characteristics, obstruction indicators, image quality, and limitations of visual assessment."
        if complaint_context:
            prompt_text += f"\nCitizen context (for reference only, do not assume true): '{complaint_context.strip()}'"

        schema = ImageEvidence.model_json_schema()

        try:
            b64_image = preprocess_image_to_base64(image_path)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": prompt_text,
                    "images": [b64_image],
                },
            ]

            parsed_json, duration = await ollama_client.chat_with_model(
                model=self.model,
                messages=messages,
                format_schema=schema,
                temperature=0.0,
            )

            evidence = ImageEvidence.model_validate(parsed_json)
            return evidence, duration

        except Exception as e:
            logger.error(f"Image evidence extraction failed: {e}")
            # Safe fallback: do not invent evidence, record extraction failure
            fallback = ImageEvidence(
                issue_candidates=["unknown"],
                visible_observations=[],
                visible_damage_characteristics=[],
                visible_obstruction_indicators=[],
                contextual_features=[],
                image_quality="unknown",
                limitations_of_visual_assessment=["Image analysis failed or was incomplete"],
                not_visually_verifiable=["Entire visual assessment unavailable due to model error"],
                extraction_error=str(e),
            )
            return fallback, 0.0

image_extractor = ImageEvidenceExtractor()
