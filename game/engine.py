import asyncio
import logging

from aiogram import Bot
from aiogram.fsm.context import FSMContext

from db.database import db
from db.questions import get_questions_for_tournament
from game.states import GameStates, GameData
from game.timer import delay, register_timer, cancel_timer


async def start_question(bot: Bot, chat_id: int, state: FSMContext) -> None:
    data: GameData = await state.get_data()
    tournament_id = data["tournament_id"]
    current_index = data["current_index"]
    with db() as conn:
        questions = get_questions_for_tournament(conn, tournament_id)
        if current_index >= len(questions):
            await bot.send_message(chat_id=chat_id, text="Турнир пройден, спасибо за игру!")
            await state.clear()
            return
        question_data = questions[current_index]
        question = (f"Вопрос {question_data['number']}\n"
                    f"{question_data['question_text']}")
        sent = await bot.send_message(chat_id=chat_id, text=question)
        await state.update_data(question_message_id=sent.message_id,
                                correct_answer=question_data['question_answer'],
                                acceptable_answers=question_data['acceptable_answers'])
        await state.set_state(GameStates.waiting_for_answer)
        async def on_timeout():
            if await state.get_state() != GameStates.waiting_for_answer:
                return
            data = await state.get_data()
            await bot.send_message(
                chat_id=chat_id,
                text=f"⏰ Время вышло. Правильный ответ: {data['correct_answer']}"
            )
            await end_round(bot, chat_id, state)
        task = asyncio.create_task(delay(60, on_timeout))
        register_timer(chat_id, task)
        logging.info(f"[{chat_id}] Вопрос {current_index + 1}/{len(questions)} отправлен")

async def end_round(bot: Bot, chat_id: int, state: FSMContext) -> None:
    data = await state.get_data()
    tournament_id = data["tournament_id"]
    next_index = data["current_index"] + 1
    await state.clear()
    cancel_timer(chat_id)
    await state.update_data(tournament_id=tournament_id, current_index=next_index)
    await start_question(bot, chat_id, state)

def is_correct(user_answer: str, correct: str, acceptable: str) -> bool:
    def norm(s: str) -> str:
        return s.strip().lower().rstrip('.,!?;:')

    u = norm(user_answer)
    if u == norm(correct):
        return True
    if acceptable:
        for alt in acceptable.split(';'):
            if norm(alt) == u:
                return True
    return False












