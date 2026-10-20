import sqlite3

def list_tournaments(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Все турниры, новые сверху — удобно для выбора."""
    return conn.execute(
        "SELECT id, name FROM tournaments ORDER BY created_at DESC"
    ).fetchall()


def get_questions_for_tournament(
    conn: sqlite3.Connection, tournament_id: int
) -> list[sqlite3.Row]:
    """Вопросы турнира в порядке игры: по номеру тура, внутри — по номеру вопроса."""
    return conn.execute(
        """
        SELECT q.*, t.number AS tour_number
        FROM questions q
        JOIN tours t ON q.tour_id = t.id
        WHERE t.tournament_id = ?
        ORDER BY t.number, q.number
        """,
        (tournament_id,)
    ).fetchall()


def get_tournament(conn: sqlite3.Connection, tournament_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT id, name FROM tournaments WHERE id = ?",
        (tournament_id,)
    ).fetchone()
