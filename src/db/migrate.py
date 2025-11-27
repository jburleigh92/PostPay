import sqlite3
from datetime import datetime


def initialize_schema(conn: sqlite3.Connection) -> None:
    """
    Create required tables if they do not already exist.

    Your original PostPay4.py used a single SQLite database to record every
    formatted Slack message that was already posted, preventing duplicates.

    This function creates the equivalent schema.
    """

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logged_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT,
            amount TEXT,
            sender TEXT,
            timestamp TEXT,
            formatted_message TEXT UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    conn.commit()
