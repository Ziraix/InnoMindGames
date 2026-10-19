import argparse
import sys
from pathlib import Path

from db.database import init_db, get_connection
from db.tournament import save_tournament
from parser.docx_parser import parse_from_docx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_DIR = PROJECT_ROOT / "data" / "source"


def load_one(conn, path: Path) -> None:
    tournament = parse_from_docx(path)
    tournament_id = save_tournament(conn, tournament)
    total_questions = sum(len(t['questions']) for t in tournament['tours'])
    print(
        f"  ✓ '{tournament['name']}' (id={tournament_id}), "
        f"туров: {len(tournament['tours'])}, "
        f"вопросов: {total_questions}"
    )


def collect_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(target.glob('*.docx'))
    raise FileNotFoundError(f"Не найдено: {target}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Загрузка турниров ЧГК из .docx в SQLite.'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default=str(DEFAULT_SOURCE_DIR),
        help='Файл .docx или папка с ними (по умолчанию data/source/)',
    )
    args = parser.parse_args()

    target = Path(args.path).resolve()
    try:
        files = collect_files(target)
    except FileNotFoundError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1

    if not files:
        print(f"В {target} нет .docx файлов")
        return 0

    init_db()

    ok, failed = 0, 0
    with get_connection() as conn:
        for f in files:
            print(f"Обработка: {f.name}")
            try:
                load_one(conn, f)
                ok += 1
            except Exception as e:
                print(f"  ✗ Ошибка: {e}", file=sys.stderr)
                failed += 1

    print(f"\nИтого: успешно {ok}, с ошибками {failed}")
    return 0 if failed == 0 else 2


if __name__ == '__main__':
    sys.exit(main())