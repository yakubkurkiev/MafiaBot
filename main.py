import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from handlers import common, game
from states import GameState
from database.service import init_db
from config import BOT_TOKEN

async def main():
    """Основная функция запуска бота"""
    # Инициализация базы данных
    init_db()
    
    # Создание бота и диспетчера
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(common.router)
    dp.include_router(game.router)
    
    # Запуск поллинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())