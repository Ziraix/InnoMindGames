from aiogram.fsm.state import State, StatesGroup
from typing import TypedDict

class GameStates(StatesGroup):
    waiting_for_answer = State()
    awaiting_judgment = State()

class GameData(TypedDict, total=False):
    tournament_id: int
    current_index: int
    question_message_id: int
    correct_answer: str
    acceptable_answers: str
    answerer_id: int
    original_answer: str
    answerer_id: int
    original_answer: str