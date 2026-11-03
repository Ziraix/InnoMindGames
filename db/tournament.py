import sqlite3


def save_tournament(conn: sqlite3.Connection, tournament: dict) -> int:
    """Сохраняет турнир. Возвращает его id.

    Повторная загрузка:
    - турнир: id сохраняется, redactors/preamble обновляются
    - туры: существующие обновляются, новые добавляются, исчезнувшие удаляются
    - вопросы: существующие обновляются, новые добавляются, исчезнувшие удаляются
    """
    with conn:
        row = conn.execute(
            """
            INSERT INTO tournaments (name, redactors, preamble) VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                redactors = excluded.redactors,
                preamble  = excluded.preamble
            RETURNING id
            """,
            (
                tournament['name'],
                ', '.join(tournament['redactors']),
                tournament['preamble'],
            )
        ).fetchone()
        tournament_id = row['id']

        incoming_tour_numbers = {t['number'] for t in tournament['tours']}
        existing_tours = {
            r['number']: r['id']
            for r in conn.execute(
                "SELECT id, number FROM tours WHERE tournament_id = ?",
                (tournament_id,)
            )
        }

        for num, old_id in existing_tours.items():
            if num not in incoming_tour_numbers:
                conn.execute("DELETE FROM tours WHERE id = ?", (old_id,))

        tour_ids: dict[int, int] = {}
        for t in tournament['tours']:
            redactors_str = ', '.join(t['redactors'])
            if t['number'] in existing_tours:
                tour_id = existing_tours[t['number']]
                conn.execute(
                    "UPDATE tours SET redactors = ?, preamble = ? WHERE id = ?",
                    (redactors_str, t['preamble'], tour_id)
                )
            else:
                cur = conn.execute(
                    "INSERT INTO tours (tournament_id, number, redactors, preamble) "
                    "VALUES (?, ?, ?, ?)",
                    (tournament_id, t['number'], redactors_str, t['preamble'])
                )
                tour_id = cur.lastrowid
            tour_ids[t['number']] = tour_id

        for t in tournament['tours']:
            tour_id = tour_ids[t['number']]
            incoming_q_numbers = {q['number'] for q in t['questions']}
            existing_q = {
                r['number']: r['id']
                for r in conn.execute(
                    "SELECT id, number FROM questions WHERE tour_id = ?",
                    (tour_id,)
                )
            }

            for num, old_id in existing_q.items():
                if num not in incoming_q_numbers:
                    conn.execute("DELETE FROM questions WHERE id = ?", (old_id,))

            for q in t['questions']:
                if q['number'] in existing_q:
                    conn.execute(
                        """
                        UPDATE questions SET
                            question_text = ?, question_answer = ?,
                            acceptable_answers = ?, comment = ?,
                            sources = ?, author = ?, unacceptable_answers = ?
                        WHERE id = ?
                        """,
                        (
                            q['question_text'], q['question_answer'],
                            q['acceptable_answers'], q['comment'],
                            q['sources'], q['author'], q['unacceptable_answers'],
                            existing_q[q['number']]
                        )
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO questions
                            (tour_id, number, question_text, question_answer,
                             acceptable_answers, comment, sources, author,
                             unacceptable_answers)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            tour_id, q['number'],
                            q['question_text'], q['question_answer'],
                            q['acceptable_answers'], q['comment'],
                            q['sources'], q['author'], q['unacceptable_answers']
                        )
                    )

    return tournament_id