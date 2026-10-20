# db/database.py
import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "questions.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tournaments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    redactors   TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tours (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id  INTEGER NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    number         INTEGER NOT NULL,
    UNIQUE (tournament_id, number)
);

CREATE TABLE IF NOT EXISTS questions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id             INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE,
    number              INTEGER NOT NULL,
    question_text       TEXT NOT NULL,
    question_answer     TEXT NOT NULL,
    acceptable_answers  TEXT NOT NULL DEFAULT '',
    comment             TEXT NOT NULL DEFAULT '',
    sources             TEXT NOT NULL DEFAULT '',
    author              TEXT NOT NULL DEFAULT '',
    UNIQUE (tour_id, number)
);

CREATE INDEX IF NOT EXISTS idx_questions_tour ON questions(tour_id);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Создаёт таблицы, если их ещё нет. Идемпотентна: можно звать сколько угодно раз."""
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)

@contextmanager
def db():
    """Открывает соединение и закрывает его после выхода из блока."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()