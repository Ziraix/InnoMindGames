from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from db.database import db
from db.questions import list_tournaments, get_tournament, get_questions_for_tournament

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
async def on_tournament_chosen(callback: CallbackQuery):
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
        f"(Игровая логика пока не подключена)"
    )
    await callback.answer()