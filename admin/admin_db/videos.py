import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "videos.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    duration INTEGER NOT NULL
    );
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)

@contextmanager
def db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def list_videos(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT id, name, duration FROM videos ORDER BY id"
    ).fetchall()

def add_video(conn: sqlite3.Connection, name: str, duration: int) -> None:
    conn.execute(
        "INSERT INTO videos (name, duration) VALUES (?, ?)", (name, duration)
    )

def delete_video(conn: sqlite3.Connection, video_id: int) -> None:
    conn.execute(
        "DELETE FROM videos WHERE id = ?", (video_id,)
    )