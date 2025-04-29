import asyncio
from aiogram import Router, Bot, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import Session, Game, Player
from states import GameStates
from keyboards import get_night_action_kb, get_voting_kb
from constants import ROLES, PHASES
from config import DISCUSSION_TIME, VOTING_TIME, NIGHT_TIME

router = Router()

@router.message(Command("startgame"))
async def start_game(message: types.Message, state: FSMContext, bot: Bot):
    with Session() as session:
        game = session.query(Game).filter_by(chat_id=message.chat.id, state="waiting").first()
        if not game:
            await message.answer("Нет активных игр в этом чате.")
            return
        
        players = session.query(Player).filter_by(game_id=game.id).all()
        if len(players) < MIN_PLAYERS:
            await message.answer(f"Недостаточно игроков. Нужно минимум {MIN_PLAYERS}.")
            return
        
        # Раздаем роли
        assign_roles(game.id)
        
        # Обновляем состояние игры
        game.state = "night"
        session.commit()
        
        # Отправляем роли игрокам
        await send_roles_to_players(bot, game.id)
        
        # Начинаем ночную фазу
        await start_night_phase(bot, game.id)
        await state.set_state(GameStates.NIGHT)

async def assign_roles(game_id):
    with Session() as session:
        players = session.query(Player).filter_by(game_id=game_id).all()
        player_count = len(players)
        
        # Определяем количество ролей
        mafia_count = 1
        detective_count = 1
        doctor_count = 1
        civilian_count = player_count - mafia_count - detective_count - doctor_count
        
        roles = []
        roles.extend(["mafia"] * mafia_count)
        roles.extend(["detective"] * detective_count)
        roles.extend(["doctor"] * doctor_count)
        roles.extend(["civilian"] * civilian_count)
        
        # Перемешиваем роли
        import random
        random.shuffle(roles)
        
        # Назначаем роли игрокам
        for i, player in enumerate(players):
            player.role = roles[i]
        
        session.commit()

async def send_roles_to_players(bot: Bot, game_id):
    with Session() as session:
        players = session.query(Player).filter_by(game_id=game_id).all()
        
        for player in players:
            role_info = ROLES[player.role]
            await bot.send_message(
                player.user_id,
                f"🎭 Ваша роль: {role_info['name']} {role_info['emoji']}\n\n"
                f"{role_info['description']}\n\n"
                "Следуйте инструкциям бота во время игры!"
            )

async def start_night_phase(bot: Bot, game_id):
    with Session() as session:
        game = session.query(Game).filter_by(id=game_id).first()
        game.current_phase = "night"
        session.commit()
        
        await bot.send_message(
            game.chat_id,
            f"{PHASES['night']}! Все засыпают...\n"
            "Просыпаются специальные роли по очереди."
        )
        
        # Даем время на ночные действия
        await asyncio.sleep(NIGHT_TIME)
        
        # Переходим к обсуждению
        await start_discussion_phase(bot, game_id)

async def start_discussion_phase(bot: Bot, game_id):
    with Session() as session:
        game = session.query(Game).filter_by(id=game_id).first()
        game.state = "discussion"
        game.current_phase = "discussion"
        session.commit()
        
        # Проверяем, кого убили
        mafia_action = session.query(Player).filter_by(game_id=game_id, role="mafia", alive=True).first()
        doctor_action = session.query(Player).filter_by(game_id=game_id, role="doctor", alive=True).first()
        
        victim = None
        if mafia_action and mafia_action.night_action_target:
            if not doctor_action or doctor_action.night_action_target != mafia_action.night_action_target:
                victim = session.query(Player).filter_by(user_id=mafia_action.night_action_target).first()
                victim.alive = False
                session.commit()
        
        if victim:
            await bot.send_message(
                game.chat_id,
                f"☠️ Ночью был убит {victim.name} ({ROLES[victim.role]['name']})!"
            )
        else:
            await bot.send_message(game.chat_id, "🌃 Этой ночью никто не погиб!")
        
        await bot.send_message(
            game.chat_id,
            f"💬 Начинается обсуждение! У вас {DISCUSSION_TIME} секунд."
        )
        
        # Таймер обсуждения
        await asyncio.sleep(DISCUSSION_TIME)
        
        # Переходим к голосованию
        await start_voting_phase(bot, game_id)

async def start_voting_phase(bot: Bot, game_id):
    with Session() as session:
        game = session.query(Game).filter_by(id=game_id).first()
        game.state = "day"
        game.current_phase = "day"
        session.commit()
        
        await bot.send_message(
            game.chat_id,
            f"{PHASES['day']}! Время голосовать.",
            reply_markup=get_voting_kb(game_id)
        )
        
        # Таймер голосования
        await asyncio.sleep(VOTING_TIME)
        
        # Подсчет голосов
        await count_votes(bot, game_id)

async def count_votes(bot: Bot, game_id):
    with Session() as session:
        game = session.query(Game).filter_by(id=game_id).first()
        players = session.query(Player).filter_by(game_id=game_id, alive=True).all()
        
        # Подсчитываем голоса
        votes = {}
        for player in players:
            if player.vote_target:
                votes[player.vote_target] = votes.get(player.vote_target, 0) + 1
        
        if votes:
            executed_id = max(votes.items(), key=lambda x: x[1])[0]
            executed = session.query(Player).filter_by(user_id=executed_id).first()
            executed.alive = False
            session.commit()
            
            await bot.send_message(
                game.chat_id,
                f"⚖️ По результатам голосования казнен {executed.name} ({ROLES[executed.role]['name']})!"
            )
        else:
            await bot.send_message(game.chat_id, "Никто не был казнен - голоса разделились!")
        
        # Проверяем условия победы
        await check_win_condition(bot, game_id)

async def check_win_condition(bot: Bot, game_id):
    with Session() as session:
        game = session.query(Game).filter_by(id=game_id).first()
        players = session.query(Player).filter_by(game_id=game_id).all()
        
        mafia_alive = sum(1 for p in players if p.role == "mafia" and p.alive)
        civilians_alive = sum(1 for p in players if p.role != "mafia" and p.alive)
        
        if mafia_alive == 0:
            await bot.send_message(
                game.chat_id,
                "🎉 Мирные жители победили! Мафия уничтожена."
            )
            game.state = "ended"
            session.commit()
        elif mafia_alive >= civilians_alive:
            await bot.send_message(
                game.chat_id,
                "🎭 Мафия победила! Мирные жители не смогли их остановить."
            )
            game.state = "ended"
            session.commit()
        else:
            # Продолжаем игру - следующая ночь
            await start_night_phase(bot, game_id)