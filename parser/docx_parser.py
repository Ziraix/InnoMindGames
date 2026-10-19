from docx import Document
from pathlib import Path

FIELD_KEYS = {
    'Зачёт': 'acceptable_answers',
    'Комментарий': 'comment',
    'Источники': 'sources',
    'Автор': 'author',
}

def get_paragraphs(document) -> list[str]:
    return [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]

def parse_from_docx(path: Path) -> dict:
    doc = Document(str(path))
    paragraphs = iter(get_paragraphs(doc))
    tournament = dict()

    tournament['name'] = next(paragraphs).strip()
    tournament['redactors'] = [redactor.strip() for redactor in next(paragraphs).removeprefix("Редакторы: ").split(',')]
    tournament['tours'] = []
    tour = None
    question = None
    while True:
        try:
            line = next(paragraphs)
        except StopIteration:
            break

        if line.startswith('Тур'):
            if tour is not None:
                if question is not None:
                    tour['questions'].append(question)
                tournament['tours'].append(tour)
                question = None
            tour_number = int(line.removeprefix('Тур'))
            tour = {'number': tour_number, 'questions': []}

        elif line.startswith('Вопрос'):
            if question is not None:
                tour['questions'].append(question)
            question_number = int(line.removeprefix('Вопрос'))
            question_text = ''
            next_line = next(paragraphs)
            while not next_line.startswith('Ответ: '):
                question_text += next_line.strip()
                next_line = next(paragraphs)
            question_answer = next_line.removeprefix('Ответ: ')
            question = {
                'number': question_number,
                'question_text': question_text,
                'question_answer': question_answer,
                'acceptable_answers': '',
                'comment': '',
                'sources': '',
                'author': ''
            }

        else:
            head, sep, tail = line.partition(':')
            if sep and head in FIELD_KEYS:
                question[FIELD_KEYS[head]] = tail.strip()
    tour['questions'].append(question)
    tournament['tours'].append(tour)
    return tournament


if __name__ == "__main__":
    path = Path(r"D:\Projects\InnoMindGames\data\source\Чемпионат Финляндии - 2022_7274.docx")
    tourn = parse_from_docx(path)
    print(tourn['tours'][0]['questions'][14])
    for tour in tourn['tours']:
        print(f"Тур {tour['number']}: {len(tour['questions'])} вопросов")