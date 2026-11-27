from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import MAIN_GROUP_ID, MAIN_THREAD_ID
from admin.states import AdminStates
from admin.admin_keyboards.admin_keyboards import message_announcement_keyboard
from admin.admin_handlers.admin import render_admin_menu

router = Router()

@router.callback_query(F.data == 'message_announcement')
async def message_announcement(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.edit_text(
        text="Отправь текст сообщения:",
        reply_markup=message_announcement_keyboard,
    )
    await callback.answer()
    await state.set_state(AdminStates.waiting_for_message)
    await state.update_data(message_announcement_id=msg.message_id)

@router.callback_query(F.data == 'message_announcement:cancel')
async def message_announcement_cancel(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    msg_id = data['message_announcement_id']
    await callback.bot.delete_message(
        chat_id = callback.message.chat.id,
        message_id = msg_id
    )
    await render_admin_menu(callback)
    await callback.answer()

@router.message(AdminStates.waiting_for_message, F.text)
async def process_message_announcement(message: Message, state: FSMContext, bot: Bot):
    await bot.copy_message(
        chat_id=MAIN_GROUP_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
        message_thread_id=MAIN_THREAD_ID,
    )
    await message.answer("✅ Отправлено")
    await state.clear()