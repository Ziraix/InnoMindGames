import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.strategy import FSMStrategy

from config import BOT_TOKEN, PROXY
from db.database import init_db
from handlers import commands, answers


async def main():
    logging.basicConfig(level=logging.INFO)

    init_db()

    if PROXY:
        session = AiohttpSession(PROXY)
        bot = Bot(token=BOT_TOKEN)
    else:
        bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(fsm_strategy=FSMStrategy.CHAT)
    dp.include_router(commands.router)
    dp.include_router(answers.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())