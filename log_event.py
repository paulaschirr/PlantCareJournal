"""
log_event.py

User-friendly logging of care events (watering, feeding, etc.)
Designed to be called from:
- CLI scripts
- Streamlit buttons
- Future agent logic
"""

import sqlite3
from datetime import date
from typing import Optional, Iterable

DB_PATH = "plants.db"


def log_event(
    plant_id: int,
    event_type: str,
    event_date: Optional[date] = None,
    notes: Optional[str] = None,
):
    """
    Log a single care event for a plant.

    Parameters
    ----------
    plant_id : int
        ID of the plant
    event_type : str
        e.g. 'watered', 'fed', 'repotted'
    event_date : date, optional
        Defaults to today
    notes : str, optional
        Free-text notes for context
    """
    event_date = event_date or date.today()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO care_log (plant_id, event_type, event_date, notes)
            VALUES (?, ?, ?, ?)
            """,
            (plant_id, event_type, event_date.isoformat(), notes),
        )
        conn.commit()


def log_bulk(
    plant_ids: Iterable[int],
    event_type: str,
    notes: Optional[str] = None,
):
    """
    Log the same event for multiple plants (e.g. 'watered all plants').

    Parameters
    ----------
    plant_ids : iterable of int
    event_type : str
    notes : str, optional
    """
    today = date.today().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            """
            INSERT INTO care_log (plant_id, event_type, event_date, notes)
            VALUES (?, ?, ?, ?)
            """,
            [(pid, event_type, today, notes) for pid in plant_ids],
        )
        conn.commit()


# --- Optional CLI usage ---
if __name__ == "__main__":
    # Example: log watering for plant 3
    log_event(
        plant_id=3,
        event_type="watered",
        notes="Soil dry; watered thoroughly"
    )

    print("Event logged.")