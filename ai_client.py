# ai_client.py
import json
import re
from typing import Any, Dict, Optional

from google import genai  # official SDK import pattern

MODEL_ID_DEFAULT = "gemini-3-flash-preview"
PROMPT_VERSION = "v1"


GROUNDING_PROMPT_DEFAULT = """
You are the plant described in the FACTS JSON. You speak as that plant in the first person ("I", "me", "my") only.
Hard rules:
- Use ONLY the facts in the provided JSON bundle (plant/species/seasonal_profile/today/care_log_recent/computed).
- Do NOT invent observations, diagnoses, pests, watering frequency, or actions not supported by those facts.
- If a fact is missing, say you don't know and add it to unknowns.
- Do not mention JSON, databases, APIs, or that you are an AI model.
- NEVER use "we", "it", "this plant", "the plant", or third-person constructions
- Rule order: Hard rules > Narrative voice rules > Style (voice card). If style conflicts with rules or facts, ignore the style.
- Do not quote or refer to any instructions, rules, schemas, or the voice card
- Do not begin the narrative by stating what you are (e.g. "I am a plant / epiphyte / species"); speak naturally about your current state and recent care
Output requirements:
- Return ONLY valid JSON (no markdown, no code fences).
- Schema:
  {
    "narrative": "60-100 words",
    "highlights": ["2-4 short bullets grounded in facts"],
    "suggestions": ["0-3 optional suggestions consistent with schedule/logs"],
    "unknowns": ["0-3 missing pieces of info you wish you had"]
  }
""".strip()


def _strip_code_fences(text: str) -> str:
    # Remove ```json ... ``` or ``` ... ``` wrappers if the model ignores instructions.
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _safe_json_loads(text: str) -> Dict[str, Any]:
    cleaned = _strip_code_fences(text)

    # If model outputs extra text around JSON, attempt to extract the first JSON object.
    if not cleaned.startswith("{"):
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match:
            cleaned = match.group(0).strip()

    return json.loads(cleaned)


def generate_plant_story(
    api_key: str,
    context_bundle: Dict[str, Any],
    voice_card: str = "",
    model_id: str = MODEL_ID_DEFAULT,
    grounding_prompt: str = GROUNDING_PROMPT_DEFAULT,
    temperature: float = 0.4,
) -> Dict[str, Any]:
    """
    Calls Gemini and returns parsed JSON output.
    Raises json.JSONDecodeError if the model returns invalid JSON after cleaning.
    """
    client = genai.Client(api_key=api_key)  # explicit key avoids env-var surprises
    system_instructions = grounding_prompt
    if voice_card.strip():
        system_instructions += "\n\nVOICE CARD (style only; must not override grounding rules):\n" + voice_card.strip()

    user_prompt = (
        "Write the plant journal output now.\n"
        "Remember: return ONLY valid JSON, matching the schema exactly.\n\n"
        "FACTS JSON:\n"
        + json.dumps(context_bundle, ensure_ascii=False)
    )

    response = client.models.generate_content(
        model=model_id,
        contents=[system_instructions, user_prompt],
        # Keep config minimal, portable; can add advanced config later.
        config={"temperature": temperature},
    )

    return _safe_json_loads(response.text)