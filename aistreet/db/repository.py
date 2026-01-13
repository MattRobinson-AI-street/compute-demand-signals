"""Database operations for sources and signals."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from aistreet.db.models import get_connection


class Source:
    """Represents a filing source."""

    def __init__(
        self,
        company: str,
        cik: str,
        form_type: str,
        filing_date: str,
        title: str,
        url: str,
        text_path: str,
        source_id: Optional[int] = None,
        source_type: str = "filing",
        created_at: Optional[str] = None,
    ):
        self.source_id = source_id
        self.company = company
        self.cik = cik
        self.form_type = form_type
        self.filing_date = filing_date
        self.source_type = source_type
        self.title = title
        self.url = url
        self.text_path = text_path
        self.created_at = created_at or datetime.utcnow().isoformat()


class Signal:
    """Represents an extracted compute demand signal."""

    def __init__(
        self,
        source_id: int,
        quote: str,
        demand_direction: str,
        segment: str,
        constraint_type: str,
        pricing: str,
        time_horizon: str,
        confidence: float,
        notes: Optional[str] = None,
        signal_id: Optional[int] = None,
        created_at: Optional[str] = None,
    ):
        self.signal_id = signal_id
        self.source_id = source_id
        self.quote = quote
        self.demand_direction = demand_direction
        self.segment = segment
        self.constraint_type = constraint_type
        self.pricing = pricing
        self.time_horizon = time_horizon
        self.confidence = confidence
        self.notes = notes
        self.created_at = created_at or datetime.utcnow().isoformat()


def insert_source(source: Source) -> Optional[int]:
    """
    Insert a source into the database.
    Returns source_id if inserted, None if already exists (idempotent).
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO sources (
                company, cik, form_type, filing_date, source_type,
                title, url, text_path, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source.company,
                source.cik,
                source.form_type,
                source.filing_date,
                source.source_type,
                source.title,
                source.url,
                source.text_path,
                source.created_at,
            ),
        )
        conn.commit()
        source_id = cursor.lastrowid
        conn.close()
        return source_id
    except sqlite3.IntegrityError:
        # Already exists (unique constraint on text_path)
        conn.close()
        return None


def get_source_by_text_path(text_path: str) -> Optional[Source]:
    """Retrieve a source by its text_path."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sources WHERE text_path = ?", (text_path,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return Source(
            source_id=row["source_id"],
            company=row["company"],
            cik=row["cik"],
            form_type=row["form_type"],
            filing_date=row["filing_date"],
            source_type=row["source_type"],
            title=row["title"],
            url=row["url"],
            text_path=row["text_path"],
            created_at=row["created_at"],
        )
    return None


def get_all_sources() -> list[Source]:
    """Retrieve all sources."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sources ORDER BY filing_date DESC")
    rows = cursor.fetchall()
    conn.close()

    return [
        Source(
            source_id=row["source_id"],
            company=row["company"],
            cik=row["cik"],
            form_type=row["form_type"],
            filing_date=row["filing_date"],
            source_type=row["source_type"],
            title=row["title"],
            url=row["url"],
            text_path=row["text_path"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


def insert_signal(signal: Signal) -> int:
    """Insert a signal into the database. Returns signal_id."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO signals (
            source_id, quote, demand_direction, segment, constraint_type,
            pricing, time_horizon, confidence, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            signal.source_id,
            signal.quote,
            signal.demand_direction,
            signal.segment,
            signal.constraint_type,
            signal.pricing,
            signal.time_horizon,
            signal.confidence,
            signal.notes,
            signal.created_at,
        ),
    )
    conn.commit()
    signal_id = cursor.lastrowid
    conn.close()
    return signal_id


def delete_signals_for_source(source_id: int) -> int:
    """Delete all signals for a given source. Returns number deleted."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM signals WHERE source_id = ?", (source_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count


def get_signals_with_sources(since_date: Optional[str] = None) -> list[dict]:
    """
    Get signals joined with their sources.
    If since_date is provided (ISO format), filter sources by filing_date >= since_date.
    Returns list of dicts with both signal and source fields.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            s.signal_id,
            s.quote,
            s.demand_direction,
            s.segment,
            s.constraint_type,
            s.pricing,
            s.time_horizon,
            s.confidence,
            s.notes,
            s.created_at as signal_created_at,
            src.source_id,
            src.company,
            src.cik,
            src.form_type,
            src.filing_date,
            src.title,
            src.url
        FROM signals s
        JOIN sources src ON s.source_id = src.source_id
    """

    params = []
    if since_date:
        query += " WHERE src.filing_date >= ?"
        params.append(since_date)

    query += " ORDER BY src.filing_date DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_signal_stats() -> dict[str, dict[str, int]]:
    """
    Get signal statistics.
    Returns dict with counts by demand_direction and constraint_type.
    """
    conn = get_connection()
    cursor = conn.cursor()

    stats = {"demand_direction": {}, "constraint_type": {}}

    # Count by demand direction
    cursor.execute(
        """
        SELECT demand_direction, COUNT(*) as count
        FROM signals
        GROUP BY demand_direction
        ORDER BY count DESC
        """
    )
    for row in cursor.fetchall():
        stats["demand_direction"][row["demand_direction"]] = row["count"]

    # Count by constraint type
    cursor.execute(
        """
        SELECT constraint_type, COUNT(*) as count
        FROM signals
        GROUP BY constraint_type
        ORDER BY count DESC
        """
    )
    for row in cursor.fetchall():
        stats["constraint_type"][row["constraint_type"]] = row["count"]

    conn.close()
    return stats
