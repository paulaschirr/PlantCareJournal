r"""
today.py

Daily "what needs doing" script:
- computes current season automatically
- fetches due watering/feeding tasks from SQLite
- prints human-friendly explanations
- supports batch logging

Run with venv python

Examples:
  .\.venv\Scripts\python.exe --log-watered 1,2,3,4
  .\.venv\Scripts\python.exe --log-fed 11
  .\.venv\Scripts\python.exe --log-watered-due
"""

import argparse
import sqlite3
from datetime import date, datetime
from typing import List, Dict, Tuple

DB_PATH = "plants.db"


def get_season(d: date) -> str:
    """Simple season mapping (Northern hemisphere)."""
    m = d.month
    if m in (12, 1, 2):
        return "winter"
    if m in (3, 4, 5):
        return "spring"
    if m in (6, 7, 8):
        return "summer"
    return "autumn"

def format_date_with_ordinal(d: date) -> str:
    day = d.day
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix} {d.strftime('%B %Y')}"

def _pretty_iso_date(iso: str) -> str:
    """Convert YYYY-MM-DD to '1st January 2026' (fallback to original)."""
    try:
        return format_date_with_ordinal(date.fromisoformat(iso))
    except Exception:
        return iso

DUE_SQL = """
WITH profile AS (
  SELECT
    p.plant_id,
    p.name,
    COALESCE(s.common_name, s.scientific_name) AS species,
    p.location,
    cp.season,
    cp.watering_days,
    cp.feeding_days,
    cp.light_preference,
    cp.notes AS profile_notes
  FROM plants p
  JOIN species s ON s.species_id = p.species_id
  JOIN care_profiles cp ON cp.plant_id = p.plant_id
  WHERE cp.season = :season
),
last_events AS (
  SELECT
    plant_id,
    MAX(CASE WHEN event_type = 'watered' THEN event_date END) AS last_watered,
    MAX(CASE WHEN event_type = 'fed' THEN event_date END) AS last_fed
  FROM care_log
  GROUP BY plant_id
),
calc AS (
  SELECT
    prof.*,
    le.last_watered,
    le.last_fed,
    CASE
      WHEN le.last_watered IS NULL THEN NULL
      ELSE CAST(julianday(:today) - julianday(le.last_watered) AS INTEGER)
    END AS days_since_watered,
    CASE
      WHEN le.last_fed IS NULL THEN NULL
      ELSE CAST(julianday(:today) - julianday(le.last_fed) AS INTEGER)
    END AS days_since_fed
  FROM profile prof
  LEFT JOIN last_events le ON le.plant_id = prof.plant_id
)

-- Water rows (all plants with watering_days)
SELECT
  plant_id, name, species, location,
  'watered' AS task_type,
  watering_days AS interval_days,
  last_watered AS last_done,
  days_since_watered AS days_since,
  CASE
    WHEN watering_days IS NULL THEN NULL
    WHEN days_since_watered IS NULL THEN 0 - watering_days
    ELSE (watering_days - days_since_watered)
  END AS days_to_due,
  CASE
    WHEN last_watered IS NULL THEN NULL
    ELSE date(last_watered, '+' || watering_days || ' days')
  END AS next_due_date,
  profile_notes AS notes
FROM calc
WHERE watering_days IS NOT NULL

UNION ALL

-- Feed rows (all plants with feeding_days)
SELECT
  plant_id, name, species, location,
  'fed' AS task_type,
  feeding_days AS interval_days,
  last_fed AS last_done,
  days_since_fed AS days_since,
  CASE
    WHEN feeding_days IS NULL THEN NULL
    WHEN days_since_fed IS NULL THEN 0 - feeding_days
    ELSE (feeding_days - days_since_fed)
  END AS days_to_due,
  CASE
    WHEN last_fed IS NULL THEN NULL
    ELSE date(last_fed, '+' || feeding_days || ' days')
  END AS next_due_date,
  profile_notes AS notes
FROM calc
WHERE feeding_days IS NOT NULL

ORDER BY task_type, plant_id;
"""


def fetch_due_tasks(today: date, season: str) -> List[sqlite3.Row]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(DUE_SQL, {"today": today.isoformat(), "season": season}).fetchall()
    return rows


def format_explanation(row: sqlite3.Row, season: str) -> str:
    """
    Agent explanation template (rule-based, explainable):
    - Decision: what to do
    - Evidence: last done + days since
    - Schedule: expected interval for season
    - Context: notes from care profile
    """
    last_done_raw = row["last_done"]
    last_done = _pretty_iso_date(last_done_raw) if last_done_raw else "never"
    days_since = row["days_since"]
    days_since_txt = f"{days_since} days ago" if days_since is not None else "never"
    return (
        f"Roughly due: every {row['interval_days']} days in {season}. "
        f"Last {row['task_type']} : {last_done} ({days_since_txt}). "
        f"Seasonal care notes: {row['notes'] or ''}".strip()
    )


def parse_id_list(s: str) -> List[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def log_events(plant_ids: List[int], event_type: str, note: str | None):
    """Insert events into care_log (batch-friendly)."""
    today = date.today().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            """
            INSERT INTO care_log (plant_id, event_type, event_date, notes)
            VALUES (?, ?, ?, ?)
            """,
            [(pid, event_type, today, note) for pid in plant_ids],
        )
        conn.commit()
