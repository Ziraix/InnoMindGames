from aiogram.fsm.state import State, StatesGroup

class GameStates(StatesGroup):
    waiting_for_answer = State()
    awaiting_judgment = State()