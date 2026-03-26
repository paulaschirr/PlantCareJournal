# log_event.py
import sqlite3
from datetime import date
from typing import Optional, Iterable

DB_PATH = "plants.db"

def _insert(conn, plant_id: int, event_type: str, event_date: date, notes: Optional[str]):
    conn.execute(
        """
        INSERT INTO care_log (plant_id, event_type, event_date, notes)
        VALUES (?, ?, ?, ?)
        """,
        (plant_id, event_type, event_date.isoformat(), notes),
    )

def log_event(
    plant_id: int,
    event_type: str,
    event_date: Optional[date] = None,
    notes: Optional[str] = None,
):
    """
    Log a single care event. If event_type == 'fed', also log a 'watered' row
    with the same timestamp and note (atomic transaction).
    """
    event_date = event_date or date.today()
    with sqlite3.connect(DB_PATH) as conn:
        # Start transaction
        _insert(conn, plant_id, event_type, event_date, notes)

        if event_type == "fed":
            # Optional de-dupe: avoid accidental double-water if a 'watered' exists at same datetime
            conn.execute(
                """
                INSERT INTO care_log (plant_id, event_type, event_date, notes)
                SELECT ?, 'watered', ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM care_log
                    WHERE plant_id = ?
                      AND event_type = 'watered'
                      AND event_date = ?
                )
                """,
                (plant_id, event_date.isoformat(), notes, plant_id, event_date.isoformat()),
            )

        conn.commit()

def log_bulk(
    plant_ids: Iterable[int],
    event_type: str,
    notes: Optional[str] = None,
):
    """
    Log the same event for multiple plants. Inherits 'fed' -> 'watered' rule.
    """
    today = date.today()
    with sqlite3.connect(DB_PATH) as conn:
        for pid in plant_ids:
            _insert(conn, pid, event_type, today, notes)
            if event_type == "fed":
                conn.execute(
                    """
                    INSERT INTO care_log (plant_id, event_type, event_date, notes)
                    SELECT ?, 'watered', ?, ?
                    WHERE NOT EXISTS (
                        SELECT 1 FROM care_log
                        WHERE plant_id = ?
                          AND event_type = 'watered'
                          AND event_date = ?
                    )
                    """,
                    (pid, today.isoformat(), notes, pid, today.isoformat()),
                )
        conn.commit()