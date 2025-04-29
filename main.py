from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import commands, game, callbacks

import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация обработчиков
dp.include_router(commands.router)
dp.include_router(game.router)
dp.include_router(callbacks.router)

async def on_startup():
    logging.info("Бот запущен")

async def on_shutdown():
    logging.info("Бот остановлен")

if __name__ == "__main__":
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.run_polling(bot)