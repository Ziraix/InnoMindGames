import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.strategy import FSMStrategy

from config import BOT_TOKEN
from db.database import init_db
from handlers import commands, answers
from admin_handlers import admin, game_announcement, message_announcement, poll_announcement


async def main():
    logging.basicConfig(level=logging.INFO)

    init_db()

    bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher(fsm_strategy=FSMStrategy.CHAT)
    dp.include_router(commands.router)
    dp.include_router(answers.router)
    dp.include_router(admin.router)
    dp.include_router(game_announcement.router)
    dp.include_router(message_announcement.router)
    dp.include_router(poll_announcement.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())