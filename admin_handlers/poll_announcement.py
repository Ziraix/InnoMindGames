from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import MAIN_GROUP_ID, THREAD_ID
from game.states import AdminStates
from keyboards.admin_keyboards import *
from db.videos import add_video, list_videos, delete_video, db

router = Router()

async def render_poll_announcement(target: CallbackQuery|Message):
    with db() as conn:
        videos = list_videos(conn)
    videos_text = '\n'.join([
            f'{idx+1}. {video['name']} ({video['duration']} мин.)'
        for idx, video in enumerate(videos)
        ])
    text = ("Текущий список видео:\n"
            f"{videos_text}")
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text=text, reply_markup=poll_admin_keyboard)
    elif isinstance(target, Message):
        await target.answer(text=text, reply_markup=poll_admin_keyboard)


@router.callback_query(F.data == 'poll_announcement')
async def poll_announcement(callback: CallbackQuery):
    await render_poll_announcement(callback)
    await callback.answer()

async def render_poll_announcement_add_video(target: CallbackQuery|Message, state: FSMContext):
    data = await state.get_data()
    text = ("Введите данные видео.\n"
            f"Название: {data.get('video_name', '')}\n"
            f"Длительность: {data.get('video_duration', '')} мин.")
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text=text, reply_markup=poll_add_video_keyboard)
    elif isinstance(target, Message):
        await target.answer(text=text, reply_markup=poll_add_video_keyboard)

@router.callback_query(F.data == "poll_announcement:add_video")
async def poll_announcement_add_video(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.poll_announcement_add_video)
    await render_poll_announcement_add_video(callback, state)
    await callback.answer()

@router.callback_query(F.data == "poll_announcement:add_video:name")
async def poll_announcement_add_video_name(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.poll_announcement_add_video_name)
    await callback.message.edit_text("Укажите название видео")
    await callback.answer()

@router.message(AdminStates.poll_announcement_add_video_name, F.text)
async def poll_announcement_add_video_name_process(message: Message, state: FSMContext):
    video_name = message.text
    await state.update_data(video_name=video_name)
    await state.set_state(AdminStates.poll_announcement_add_video)
    await render_poll_announcement_add_video(message, state)

@router.callback_query(F.data == "poll_announcement:add_video:duration")
async def poll_announcement_add_video_duration(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.poll_announcement_add_video_duration)
    await callback.message.edit_text("Укажите длительность видео (в минутах)")
    await callback.answer()


@router.message(AdminStates.poll_announcement_add_video_duration, F.text.isdigit())
async def poll_announcement_add_video_duration_process(message: Message, state: FSMContext):
    video_duration = int(message.text)
    await state.update_data(video_duration=video_duration)
    await state.set_state(AdminStates.poll_announcement_add_video)
    await render_poll_announcement_add_video(message, state)

@router.callback_query(F.data == "poll_announcement:add_video:save")
async def poll_announcement_add_video_save(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    with db() as conn:
        add_video(conn, data['video_name'], data['video_duration'])
    await state.clear()
    await render_poll_announcement(callback)
    await callback.answer()

@router.callback_query(F.data == 'poll_announcement:delete_video')
async def poll_announcement_delete_video(callback: CallbackQuery):
    with db() as conn:
        videos = list_videos(conn)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=video_name, callback_data=f'poll_announcement:delete_video:id:{video_id}')]
        for video_id, video_name, duration in videos
    ])

    await callback.message.edit_text(
        text='Выберите видео для удаления',
        reply_markup=keyboard,
    )
    await callback.answer()

@router.callback_query(F.data.startswith('poll_announcement:delete_video:id:'))
async def poll_announcement_delete_video_id(callback: CallbackQuery):
    video_id = int(callback.data.removeprefix('poll_announcement:delete_video:id:'))
    with db() as conn:
        delete_video(conn, video_id)
    await render_poll_announcement(callback)
    await callback.answer()

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
        question="Что смотрим в следующий раз?",
        is_anonymous=False,
        allows_multiple_answers=True
    )
    await callback.message.edit_text("Опрос отправлен!")
    await callback.answer()