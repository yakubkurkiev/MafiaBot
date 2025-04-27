from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from random import sample
from typing import Optional

from database.service import (
    get_game_by_chat_id, create_game, add_player,
    get_players_in_game, update_player_role
)
from states import GameState
from keyboards import get_game_menu, get_vote_keyboard
from config import ROLES

router = Router()

@router.message(F.text == "🎮 Начать игру")
async def start_game(message: types.Message, state: FSMContext):
    """Начало новой игры"""
    chat_id = message.chat.id
    game = get_game_by_chat_id(chat_id)
    
    if game and game.is_active:
        await message.answer("Игра уже идет в этом чате!")
        return
    
    if not game:
        game = create_game(chat_id)
    
    # Добавляем первого игрока (того, кто начал игру)
    await add_player_to_game(message.from_user.id, message.from_user.username, game.id)
    
    await message.answer(
        "Игра начата! Ожидаем игроков...\n"
        "Для присоединения к игре отправьте /join",
        reply_markup=get_game_menu()
    )
    await state.set_state(GameState.waiting_for_players)

async def add_player_to_game(user_id: int, username: str, game_id: int) -> None:
    """Добавление игрока в игру"""
    players = get_players_in_game(game_id)
    if any(p.user_id == user_id for p in players):
        return
    
    add_player(game_id, user_id, username)

@router.message(Command("join"))
async def join_game(message: types.Message, state: FSMContext):
    """Присоединение к игре"""
    current_state = await state.get_state()
    if current_state != GameState.waiting_for_players:
        await message.answer("Сейчас нельзя присоединиться к игре.")
        return
    
    game = get_game_by_chat_id(message.chat.id)
    if not game:
        await message.answer("Игра не найдена. Сначала начните игру.")
        return
    
    await add_player_to_game(message.from_user.id, message.from_user.username, game.id)
    players = get_players_in_game(game.id)
    await message.answer(f"Игрок {message.from_user.username} присоединился! Всего игроков: {len(players)}")

@router.message(F.text == "🏁 Завершить игру")
async def end_game(message: types.Message, state: FSMContext):
    """Досрочное завершение игры"""
    await state.clear()
    await message.answer("Игра завершена!", reply_markup=get_main_menu())

@router.message(F.text == "👥 Список игроков")
async def show_players(message: types.Message):
    """Показать список игроков"""
    game = get_game_by_chat_id(message.chat.id)
    if not game:
        await message.answer("Игра не найдена.")
        return
    
    players = get_players_in_game(game.id)
    if not players:
        await message.answer("Нет игроков в игре.")
        return
    
    players_list = "\n".join([f"👤 {p.username}" for p in players])
    await message.answer(f"Игроки в игре:\n{players_list}")

@router.message(F.text == "▶️ Начать игру")
async def start_game_session(message: types.Message, state: FSMContext):
    """Начать игровую сессию после сбора игроков"""
    game = get_game_by_chat_id(message.chat.id)
    if not game:
        await message.answer("Игра не найдена.")
        return
    
    players = get_players_in_game(game.id)
    if len(players) < sum(ROLES.values()):
        await message.answer(f"Недостаточно игроков. Нужно минимум {sum(ROLES.values())}.")
        return
    
    # Распределяем роли
    assign_roles(game.id, players)
    
    await message.answer("Игра началась! Наступает ночь...")
    await state.set_state(GameState.night)
    await night_actions(message, players)

def assign_roles(game_id: int, players: list) -> None:
    """Распределение ролей между игроками"""
    roles = []
    for role, count in ROLES.items():
        roles.extend([role] * count)
    
    # Если игроков больше, чем ролей, добавляем мирных жителей
    while len(players) > len(roles):
        roles.append("civilian")
    
    # Перемешиваем роли и назначаем игрокам
    shuffled_roles = sample(roles, len(roles))
    for player, role in zip(players, shuffled_roles):
        update_player_role(player.id, role)

async def night_actions(message: types.Message, players: list) -> None:
    """Обработка ночных действий"""
    # Здесь должна быть логика ночных действий (мафия убивает, доктор лечит)
    # В упрощенной версии просто переходим к дню
    await message.answer("Ночь прошла. Наступает день!")
    alive_players = [p for p in players if p.is_alive]
    await message.answer(
        "Обсудите кто может быть мафией и проголосуйте!",
        reply_markup=get_vote_keyboard(alive_players)
    )