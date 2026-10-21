from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from game.engine import end_round, is_correct
from game.states import GameStates
from game.timer import cancel_timer

router = Router()


@router.message(GameStates.waiting_for_answer, F.reply_to_message)
async def on_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.reply_to_message.message_id != data.get('question_message_id'):
        return

    cancel_timer(message.chat.id)

    user_answer = message.text.strip() if message.text else ''
    correct = data['correct_answer']
    acceptable = data.get('acceptable_answers', '')

    if is_correct(user_answer, correct, acceptable):
        await message.reply(f"✅ Правильно! Ответ: {correct}")
        await end_round(message.bot, message.chat.id, state)
        return

    # не совпало — суд
    await state.update_data(
        answerer_id=message.from_user.id,
        original_answer=user_answer,
    )
    await state.set_state(GameStates.awaiting_judgment)
    buttons = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Да", callback_data="judge:yes"),
        InlineKeyboardButton(text="Нет", callback_data="judge:no"),
    ]])
    await message.reply(
        f"Правильный ответ: {correct}\n"
        f"Твой ответ: «{user_answer}»\n\n"
        f"Считаем правильным?",
        reply_markup=buttons,
    )


@router.callback_query(GameStates.awaiting_judgment, F.data.startswith('judge:'))
async def on_judgment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.from_user.id != data.get('answerer_id'):
        await callback.answer("Это не твой ответ", show_alert=True)
        return

    verdict = callback.data.split(':', 1)[1]
    prefix = "✅ Засчитано" if verdict == 'yes' else "❌ Не засчитано"
    await callback.message.edit_text(
        f"{prefix}. Правильный ответ: {data['correct_answer']}",
        reply_markup=None,
    )
    await callback.answer()
    await end_round(callback.bot, callback.message.chat.id, state)