import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "study_assistant.db"

def get_connection(db_path=DB_PATH):
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as exc:
        raise RuntimeError(f"Could not connect to database: {exc}") from exc

def initialize_database(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                study_hours REAL NOT NULL CHECK(study_hours >= 0),
                tasks_completed INTEGER NOT NULL CHECK(tasks_completed >= 0),
                session_date TEXT NOT NULL
            )
        """)
        conn.commit()
