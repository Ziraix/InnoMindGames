from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import MAIN_GROUP_ID, THREAD_ID
from game.states import AdminStates
from keyboards.admin_keyboards import *
from db.videos import *

router = Router()

@router.callback_query(F.data == 'poll_announcement')
async def poll_announcement(callback: CallbackQuery):
    with db() as conn:
        videos = list_videos(conn)
    videos_text = '\n'.join([f'{video_id}. {name} ({duration} мин.)' for video_id, name, duration in videos])
    text = ("Текущий список видео:\n"
            f"{videos_text}")
    await callback.message.edit_text(text=text, reply_markup=poll_admin_keyboard)


@router.callback_query(F.data == 'poll_announcement:send')
async def poll_announcement_send(callback: CallbackQuery, bot: Bot):
    with db() as conn:
        videos = list_videos(conn)

    if not (2 <= len(videos) <= 10):
        await callback.answer(
            f"Для опроса нужно 2–10 видео, а в базе {len(videos)}",
            show_alert=True,
        )
        return

    await bot.send_poll(
        chat_id=MAIN_GROUP_ID,
        message_thread_id=THREAD_ID,
        options=[f'{name} ({duration} мин.)' for video_id, name, duration in videos],
        question="Что смотрим в следующий раз?"
    )
    await callback.message.edit_text("Опрос отправлен!")
    await callback.answer()