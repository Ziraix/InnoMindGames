from docx import Document
from pathlib import Path
import re

FIELD_KEYS = {
    'Ответ': 'question_answer',
    'Зачёт': 'acceptable_answers',
    'Незачёт': 'unacceptable_answers',
    'Комментарий': 'comment',
    'Источники': 'sources',
    'Источник': 'sources',
    'Автор': 'author',
}

def get_paragraphs(document) -> list[str]:
    return [paragraph.text.replace('\u00a0', ' ').strip() for paragraph in document.paragraphs if paragraph.text.strip()]

def get_text(document) -> str:
    return '\n'.join(get_paragraphs(document))

def divide_by_tours(tournament_text: str) -> list[str]:
    pattern = r'(?=Тур\s*\d+)'
    tours = re.split(pattern, tournament_text)
    return tours

def divide_by_questions(tour_text: str) -> list[str]:
    pattern = r'(?=Вопрос\s*\d+)'
    questions = re.split(pattern, tour_text)
    return questions

def parse_question(full_question: str) -> dict:
    lines = full_question.split('\n')
    lines_iter = iter(lines)
    number = int(next(lines_iter).removeprefix('Вопрос '))
    question = {'number': number,
                'question_text': '',
                'question_answer': '',
                'acceptable_answers': '',
                'unacceptable_answers': '',
                'comment': '',
                'sources': '',
                'author': ''}
    question_text = []
    for line in lines_iter:
        head, sep, tail = line.partition(':')
        if sep and head in FIELD_KEYS:
            question[FIELD_KEYS[head]] = tail.strip()
        else:
            question_text.append(line)
    question['question_text'] = '\n'.join(question_text)
    return question

def parse_tour(full_tour: str) -> dict:
    raw_questions = iter(divide_by_questions(full_tour))
    head = iter(next(raw_questions).split('\n'))
    number = int(next(head).removeprefix('Тур '))
    redactors = []
    preamble = []
    for line in head:
        if line.startswith('Редакторы: '):
            redactors = [
                r.strip()
                for r in line.removeprefix('Редакторы:').split(',')
                if r.strip()
            ]
        else:
            preamble.append(line)
    preamble = '\n'.join(preamble)
    questions = []
    for raw_question in raw_questions:
        questions.append(parse_question(raw_question))
    return {'redactors': redactors,
            'questions': questions,
            'preamble': preamble,
            'number': number, }

def parse_tournament(full_tournament: str) -> dict:
    raw_tours = divide_by_tours(full_tournament)
    raw_tours_iter = iter(raw_tours)
    head = next(raw_tours_iter).split('\n')
    tournament_name = head[0].strip()
    redactors = [
        r.strip()
        for r in head[1].removeprefix('Редакторы:').split(',')
        if r.strip()
    ]
    preamble = []
    tours = []
    for i in range(2, len(head)):
        preamble.append(head[i].strip())
    preamble = '\n'.join(preamble)
    for raw_tour in raw_tours_iter:
        tour = parse_tour(raw_tour)
        tours.append(tour)
    return {
        'name': tournament_name,
        'redactors': redactors,
        'tours': tours,
        'preamble': preamble
    }

def parse_from_docx(path: Path) -> dict:
    doc = Document(str(path))
    tournament_text = get_text(doc)
    return parse_tournament(tournament_text)
