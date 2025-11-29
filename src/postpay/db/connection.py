import sqlite3


def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Create and return a SQLite connection.

    This mirrors the behavior in your original PostPay4.py, where a single
    sqlite3 connection was created and reused for all logging and duplicate checks.

    Args:
        db_path: Path to SQLite file, e.g. data/logged_payments.db

    Returns:
        sqlite3.Connection object
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # allows convenient dict-like row access
    return conn
