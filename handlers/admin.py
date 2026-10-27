from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram3_calendar import SimpleCalendar, simple_cal_callback

from config import ADMINS_ID, MAIN_GROUP_ID, THREAD_ID, SUB_THREAD_ID
from game.states import AdminStates
from keyboards.admin_keyboards import *

router = Router()

calendar = SimpleCalendar()

MONTHS_GENITIVE = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря",
}

WEEKDAYS = {
    0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг",
    4: "Пятница", 5: "Суббота", 6: "Воскресенье",
}

@router.message(Command('admin'))
async def admin(message: Message):
    if message.from_user is None:
        return
    if message.from_user.id not in ADMINS_ID:
        await message.answer("У вас нет прав на использование этой команды")
        return
    await message.answer(
        text="Приветствую, мой господин. Что пожелаете?\n",
        reply_markup = main_admin_menu
    )

@router.callback_query(F.data == 'message_announcement')
async def message_announcement(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Отправь текст сообщения:")
    await callback.answer()
    await state.set_state(AdminStates.waiting_for_message)

@router.message(AdminStates.waiting_for_message, F.text)
async def process_message_announcement(message: Message, state: FSMContext, bot: Bot):
    await bot.copy_message(
        chat_id=MAIN_GROUP_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
        message_thread_id=THREAD_ID,
    )
    await message.answer("✅ Отправлено")
    await state.clear()

async def render_game_announcement(target: CallbackQuery|Message, state: FSMContext):
    data = await state.get_data()
    photo_id = data.get('photo_id', None)
    text = ("Введите данные об игре.\n"
             f"Название: {data.get('name', '')}\n"
             f"Дата и время: {data.get('date', '')} {data.get('time', '')}\n"
             f"Локация: {data.get('location', '')}\n"
             f"Картинка: {"Загружена" if photo_id else "Не загружена"}")
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text=text, reply_markup=game_announcement_keyboard)
    elif isinstance(target, Message):
        await target.answer(text=text, reply_markup=game_announcement_keyboard)

@router.callback_query(F.data == 'game_announcement')
async def game_announcement(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.game_announcement)
    await render_game_announcement(callback, state)
    await callback.answer()

@router.callback_query(F.data == 'game_announcement:date')
async def game_announcement_date(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выбери дату:",
        reply_markup=await calendar.start_calendar()
    )
    await callback.answer()

@router.callback_query(simple_cal_callback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await calendar.process_selection(callback, callback_data)
    if selected:
        await state.update_data(date=f"{WEEKDAYS[date.weekday()].upper()} ({date.day} {MONTHS_GENITIVE[date.month]})")
        await render_game_announcement(callback, state)
    await callback.answer()

@router.callback_query(F.data == 'game_announcement:time')
async def game_announcement_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='Укажите время в формате hh:mm'
    )
    await state.set_state(AdminStates.game_announcement_time)
    await state.update_data(original_message=callback.message)
    await callback.answer()

@router.message(AdminStates.game_announcement_time, F.text)
async def game_announcement_time_process(message: Message, state: FSMContext):
    time = message.text
    data = await state.get_data()
    original_message = data['original_message']
    await state.update_data(time=time)
    await state.set_state(AdminStates.game_announcement)
    await original_message.delete()
    await render_game_announcement(message, state)

@router.callback_query(F.data == 'game_announcement:name')
async def game_announcement_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='Укажите название игры'
    )
    await state.set_state(AdminStates.game_announcement_name)
    await state.update_data(original_message=callback.message)
    await callback.answer()

@router.message(AdminStates.game_announcement_name, F.text)
async def game_announcement_name_process(message: Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    original_message = data['original_message']
    await state.update_data(name=name)
    await state.set_state(AdminStates.game_announcement)
    await original_message.delete()
    await render_game_announcement(message, state)

@router.callback_query(F.data == 'game_announcement:location')
async def game_announcement_location(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='Укажите место игры'
    )
    await state.set_state(AdminStates.game_announcement_location)
    await state.update_data(original_message=callback.message)
    await callback.answer()

@router.message(AdminStates.game_announcement_location, F.text)
async def game_announcement_location_process(message: Message, state: FSMContext):
    location = message.text
    data = await state.get_data()
    original_message = data['original_message']
    await state.update_data(location=location)
    await state.set_state(AdminStates.game_announcement)
    await original_message.delete()
    await render_game_announcement(message, state)

@router.callback_query(F.data == 'game_announcement:picture')
async def game_announcement_picture(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='Укажите картинку'
    )
    await state.set_state(AdminStates.game_announcement_picture)
    await state.update_data(original_message=callback.message)
    await callback.answer()

@router.message(AdminStates.game_announcement_picture, F.photo)
async def game_announcement_picture_process(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    original_message = data['original_message']
    await state.update_data(photo_id=photo_id)
    await state.set_state(AdminStates.game_announcement)
    await original_message.delete()
    await render_game_announcement(message, state)

@router.callback_query(F.data == 'game_announcement:send')
async def game_announcement_send(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    announcement = (f"📗{data['date']}📗\n"
                    f"Что❓ {data['name']}\n"
                    f"Где❓ {data['location']}\n"
                    f"Когда❓ {data['time']}\n")
    await bot.send_photo(
        chat_id=MAIN_GROUP_ID,
        message_thread_id=THREAD_ID,
        caption=announcement,
        photo=data['photo_id']
    )
    if SUB_THREAD_ID:
        await bot.send_photo(
            chat_id=MAIN_GROUP_ID,
            message_thread_id=SUB_THREAD_ID,
            caption=announcement,
            photo=data['photo_id']
        )
    await callback.message.edit_text("✅ Анонс опубликован")
    await state.clear()
    await callback.answer()