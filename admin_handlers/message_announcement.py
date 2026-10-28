from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import MAIN_GROUP_ID, THREAD_ID
from game.states import AdminStates

router = Router()

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