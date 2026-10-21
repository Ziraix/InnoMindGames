from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from db.database import db
from db.questions import list_tournaments, get_tournament, get_questions_for_tournament
from game.engine import start_question

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для игры в ЧГК.\n\n"
        "/tournaments — список турниров"
    )


@router.message(Command('tournaments'))
async def cmd_tournaments(message: Message):
    with db() as conn:
        tournaments = list_tournaments(conn)

    if not tournaments:
        await message.answer("В базе пока нет турниров.")
        return

    buttons = [
        [InlineKeyboardButton(text=t['name'], callback_data=f"tour:{t['id']}")]
        for t in tournaments
    ]
    await message.answer(
        "Выбери турнир:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith('tour:'))
async def on_tournament_chosen(callback: CallbackQuery, state: FSMContext, bot: Bot):
    tournament_id = int(callback.data.split(':', 1)[1])

    with db() as conn:
        tournament = get_tournament(conn, tournament_id)
        questions = get_questions_for_tournament(conn, tournament_id)

    if tournament is None:
        await callback.answer("Турнир не найден", show_alert=True)
        return

    await callback.message.edit_text(
        f"Турнир: {tournament['name']}\n"
        f"Вопросов: {len(questions)}\n\n"
    )
    await callback.answer()

    await state.update_data(tournament_id=tournament_id, current_index=0)
    await start_question(bot, callback.message.chat.id, state)

@router.message(Command('play'))
async def cmd_play(message: Message, state: FSMContext, bot: Bot):
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip().isdigit():
        await message.answer("Использование: /play <id турнира>")
        return

    tournament_id = int(args[1].strip())

    # проверим, что турнир существует
    with db() as conn:
        tournament = get_tournament(conn, tournament_id)

    if tournament is None:
        await message.answer(f"Турнир с id={tournament_id} не найден")
        return

    await state.update_data(tournament_id=tournament_id, current_index=0)
    await message.answer(f"Начинаем: {tournament['name']}")
    await start_question(bot, message.chat.id, state)