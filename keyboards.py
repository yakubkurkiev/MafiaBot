from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

def get_main_menu() -> ReplyKeyboardMarkup:
    """Клавиатура главного меню"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎮 Начать игру")
    builder.button(text="ℹ️ Правила")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_game_menu() -> ReplyKeyboardMarkup:
    """Клавиатура во время игры"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="👥 Список игроков")
    builder.button(text="🏁 Завершить игру")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_vote_keyboard(players: list) -> ReplyKeyboardMarkup:
    """Клавиатура для голосования"""
    builder = ReplyKeyboardBuilder()
    for player in players:
        builder.button(text=f"🗳 {player.username}")
    builder.button(text="🚫 Пропустить")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)