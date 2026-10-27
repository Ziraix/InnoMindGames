from aiogram.fsm.state import State, StatesGroup

class GameStates(StatesGroup):
    waiting_for_answer = State()
    awaiting_judgment = State()

class AdminStates(StatesGroup):
    waiting_for_message = State()
    game_announcement = State()
    game_announcement_time = State()
    game_announcement_name = State()
    game_announcement_location = State()
    game_announcement_picture = State()