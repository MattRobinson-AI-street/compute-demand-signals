"""Database schema and connection management."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from aistreet.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_db() -> None:
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create sources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            source_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            cik TEXT NOT NULL,
            form_type TEXT NOT NULL,
            filing_date TEXT NOT NULL,
            source_type TEXT NOT NULL DEFAULT 'filing',
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            text_path TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            CHECK (form_type IN ('8-K', '10-Q', '10-K')),
            CHECK (source_type = 'filing')
        )
    """)

    # Create signals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            quote TEXT NOT NULL,
            demand_direction TEXT NOT NULL,
            segment TEXT NOT NULL,
            constraint_type TEXT NOT NULL,
            pricing TEXT NOT NULL,
            time_horizon TEXT NOT NULL,
            confidence REAL NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (source_id) REFERENCES sources (source_id) ON DELETE CASCADE,
            CHECK (demand_direction IN ('up', 'down', 'flat', 'unclear')),
            CHECK (segment IN ('training', 'inference', 'general')),
            CHECK (constraint_type IN ('power', 'chips', 'networking', 'capacity', 'other', 'none')),
            CHECK (pricing IN ('up', 'down', 'stable', 'unclear')),
            CHECK (time_horizon IN ('now', 'next_qtr', '6_12mo', '12mo_plus', 'unclear')),
            CHECK (confidence >= 0.0 AND confidence <= 1.0)
        )
    """)

    # Create indexes for common queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sources_filing_date
        ON sources(filing_date DESC)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sources_cik
        ON sources(cik)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_signals_source_id
        ON signals(source_id)
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
