from aiogram import Router, types
from aiogram.filters import Command
from keyboards import get_main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "Добро пожаловать в игру Мафия!\n"
        "Используйте меню для управления игрой.",
        reply_markup=get_main_menu()
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        "🔹 Правила игры Мафия:\n\n"
        "1. Игра проходит в несколько этапов: ночь и день.\n"
        "2. Ночью мафия выбирает жертву, а доктор может кого-то спасти.\n"
        "3. Днём игроки обсуждают и голосуют за подозреваемого.\n"
        "4. Цель мирных жителей - вычислить и устранить мафию.\n"
        "5. Цель мафии - устранить всех мирных жителей."
    )