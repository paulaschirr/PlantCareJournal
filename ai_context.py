# ai_context.py
import sqlite3
from datetime import date
from typing import Any, Dict, Optional, Tuple

DB_PATH = "plants.db"


def _sanitize_weather_for_ai(raw):
    """
    Keep only what the plant can 'see' outside.
    Returns: {"description": "..."} or None.
    """
    if not raw or not isinstance(raw, dict):
        return None
    desc = (raw.get("description") or "").strip()
    return {"description": desc} if desc else None

def _row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    return dict(row) if row is not None else None


def get_plant_context_bundle(
    plant_id: int,
    season: str,
    today: Optional[date] = None,
    weather: Optional[Dict[str, Any]] = None,
    log_limit: int = 10,
) -> Tuple[Dict[str, Any], str, int]:
    """
    Returns:
      context_bundle: dict of allowed facts (plant/species/seasonal profile/recent logs + computed)
      voice_card: species.personality_prompt (fallback to empty string)
      last_log_id: MAX(care_log.log_id) for stable caching key (0 if none)
    """
    today = today or date.today()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        # Plant + species + seasonal care profile (for the current season)
        profile = conn.execute(
            """
            SELECT
              p.plant_id,
              p.name,
              p.location,
              p.notes AS plant_notes,

              s.species_id,
              s.common_name,
              s.scientific_name,
              s.native_climate,
              s.care_context,
              s.personality_prompt,

              cp.season,
              cp.watering_days,
              cp.feeding_days,
              cp.light_preference,
              cp.notes AS seasonal_notes
            FROM plants p
            JOIN species s ON s.species_id = p.species_id
            LEFT JOIN care_profiles cp
              ON cp.plant_id = p.plant_id AND cp.season = ?
            WHERE p.plant_id = ?
            """,
            (season, plant_id),
        ).fetchone()

        # Recent care log entries (deterministic ordering)
        logs = conn.execute(
            """
            SELECT log_id, event_type, event_date, notes
            FROM care_log
            WHERE plant_id = ?
            ORDER BY event_date DESC, log_id DESC
            LIMIT ?
            """,
            (plant_id, log_limit),
        ).fetchall()

        # Cache marker: changes with every insert
        last_log_id_row = conn.execute(
            "SELECT COALESCE(MAX(log_id), 0) AS last_log_id FROM care_log WHERE plant_id = ?",
            (plant_id,),
        ).fetchone()
        last_log_id = int(last_log_id_row["last_log_id"]) if last_log_id_row else 0

        # Also handy: last event date (for display only; can't rely on it for cache invalidation, as multiple logs could be added on the same day)
        last_event_date_row = conn.execute(
            "SELECT MAX(event_date) AS last_event_date FROM care_log WHERE plant_id = ?",
            (plant_id,),
        ).fetchone()
        last_event_date = last_event_date_row["last_event_date"] if last_event_date_row else None

    profile_dict = _row_to_dict(profile) or {"plant_id": plant_id}
    voice_card = (profile_dict.get("personality_prompt") or "").strip()

    context_bundle: Dict[str, Any] = {
        "plant": {
            "plant_id": profile_dict.get("plant_id"),
            "name": profile_dict.get("name"),
            "location": profile_dict.get("location"),
            "notes": profile_dict.get("plant_notes"),
        },
        "species": {
            "common_name": profile_dict.get("common_name"),
            "scientific_name": profile_dict.get("scientific_name"),
            "native_climate": profile_dict.get("native_climate"),
            "care_context": profile_dict.get("care_context"),
        },
        "seasonal_profile": {
            "season": season,
            "watering_days": profile_dict.get("watering_days"),
            "feeding_days": profile_dict.get("feeding_days"),
            "light_preference": profile_dict.get("light_preference"),
            "notes": profile_dict.get("seasonal_notes"),
        },
        "today": {
            "date": today.isoformat(),
            "season": season,
            "weather": _sanitize_weather_for_ai(weather),  
        },
        "care_log_recent": [dict(r) for r in logs],
        "computed": {
            "last_event_date": last_event_date,
            "last_log_id": last_log_id,
            "log_count_included": len(logs),
        },
    }

    return context_bundle, voice_card, last_log_id