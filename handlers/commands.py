from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import Session, Game, Player
from states import GameStates
from keyboards import get_join_keyboard
from config import MIN_PLAYERS, MAX_PLAYERS

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎭 Добро пожаловать в игру Мафия!\n"
        "Добавьте меня в группу и используйте /newgame для создания игры.",
        reply_markup=get_join_keyboard()
    )

@router.message(Command("newgame"))
async def new_game(message: types.Message, state: FSMContext):
    if message.chat.type != "group" and message.chat.type != "supergroup":
        await message.answer("Игра возможна только в групповом чате!")
        return
    
    with Session() as session:
        # Проверяем, есть ли активная игра
        existing_game = session.query(Game).filter_by(chat_id=message.chat.id, state="waiting").first()
        if existing_game:
            await message.answer("Игра уже создана! Используйте /join для присоединения.")
            return
        
        # Создаем новую игру
        game = Game(chat_id=message.chat.id, state="waiting")
        session.add(game)
        session.commit()
        
        # Добавляем создателя в игру
        player = Player(
            user_id=message.from_user.id,
            name=message.from_user.first_name,
            game_id=game.id
        )
        session.add(player)
        session.commit()
        
        await message.answer(
            f"🎮 Новая игра создана! Необходимо минимум {MIN_PLAYERS} игроков.\n"
            "Используйте /join для присоединения.",
            reply_markup=get_join_keyboard()
        )
        await state.set_state(GameStates.WAITING)

@router.message(Command("join"))
async def join_game(message: types.Message, state: FSMContext):
    with Session() as session:
        # Ищем активную игру в этом чате
        game = session.query(Game).filter_by(chat_id=message.chat.id, state="waiting").first()
        if not game:
            await message.answer("Нет активных игр в этом чате. Создайте новую с помощью /newgame")
            return
        
        # Проверяем, не присоединился ли уже игрок
        existing_player = session.query(Player).filter_by(user_id=message.from_user.id, game_id=game.id).first()
        if existing_player:
            await message.answer("Вы уже в игре!")
            return
        
        # Проверяем максимальное количество игроков
        player_count = session.query(Player).filter_by(game_id=game.id).count()
        if player_count >= MAX_PLAYERS:
            await message.answer(f"Достигнуто максимальное количество игроков ({MAX_PLAYERS})")
            return
        
        # Добавляем игрока
        player = Player(
            user_id=message.from_user.id,
            name=message.from_user.first_name,
            game_id=game.id
        )
        session.add(player)
        session.commit()
        
        await message.answer(f"✅ {message.from_user.first_name} присоединился к игре!")
        
        # Проверяем, можно ли начинать игру
        if player_count + 1 >= MIN_PLAYERS:
            await message.answer(f"Достаточно игроков! Используйте /startgame для начала.")