from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import ADMINS_ID
from admin.admin_keyboards.admin_keyboards import *

router = Router()

@router.message(Command('admin'))
async def admin(message: Message):
    if message.from_user is None:
        return
    if message.from_user.id not in ADMINS_ID:
        await message.answer("У вас нет прав на использование этой команды")
        return
    await render_admin_menu(message)

async def render_admin_menu(target: Message|CallbackQuery):
    text = "Приветствую, мой господин. Что пожелаете?\n"
    reply_markup = main_admin_menu
    await target.answer(
        text=text,
        reply_markup=reply_markup
    )