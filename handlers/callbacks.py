from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from database import Session, Player, Game
from states import GameStates
from keyboards import get_night_action_kb

router = Router()

@router.callback_query(F.data == "join_game")
async def join_game_callback(callback: types.CallbackQuery, state: FSMContext):
    # Обработка нажатия кнопки "Присоединиться"
    with Session() as session:
        game = session.query(Game).filter_by(chat_id=callback.message.chat.id, state="waiting").first()
        if not game:
            await callback.answer("Нет активных игр в этом чате.")
            return
        
        existing_player = session.query(Player).filter_by(user_id=callback.from_user.id, game_id=game.id).first()
        if existing_player:
            await callback.answer("Вы уже в игре!")
            return
        
        player = Player(
            user_id=callback.from_user.id,
            name=callback.from_user.first_name,
            game_id=game.id
        )
        session.add(player)
        session.commit()
        
        await callback.message.answer(f"✅ {callback.from_user.first_name} присоединился к игре!")
        await callback.answer()

@router.callback_query(F.data.startswith("mafia_select:"))
async def mafia_select_target(callback: types.CallbackQuery, state: FSMContext):
    # Мафия выбирает жертву
    target_id = int(callback.data.split(":")[1])
    
    with Session() as session:
        player = session.query(Player).filter_by(user_id=callback.from_user.id).first()
        if not player or player.role != "mafia":
            await callback.answer("Вы не мафия!")
            return
        
        player.night_action_target = target_id
        session.commit()
        
        target = session.query(Player).filter_by(user_id=target_id).first()
        await callback.message.edit_text(f"✅ Вы выбрали {target.name} в качестве жертвы.")
        await callback.answer()

@router.callback_query(F.data.startswith("doctor_select:"))
async def doctor_select_target(callback: types.CallbackQuery, state: FSMContext):
    # Доктор выбирает кого лечить
    target_id = int(callback.data.split(":")[1])
    
    with Session() as session:
        player = session.query(Player).filter_by(user_id=callback.from_user.id).first()
        if not player or player.role != "doctor":
            await callback.answer("Вы не доктор!")
            return
        
        player.night_action_target = target_id
        session.commit()
        
        target = session.query(Player).filter_by(user_id=target_id).first()
        await callback.message.edit_text(f"✅ Вы решили вылечить {target.name}.")
        await callback.answer()

@router.callback_query(F.data.startswith("detective_select:"))
async def detective_select_target(callback: types.CallbackQuery, state: FSMContext):
    # Детектив проверяет игрока
    target_id = int(callback.data.split(":")[1])
    
    with Session() as session:
        player = session.query(Player).filter_by(user_id=callback.from_user.id).first()
        if not player or player.role != "detective":
            await callback.answer("Вы не детектив!")
            return
        
        target = session.query(Player).filter_by(user_id=target_id).first()
        await callback.message.edit_text(f"🔍 {target.name} - {ROLES[target.role]['name']}")
        await callback.answer()

@router.callback_query(F.data.startswith("vote:"))
async def vote_for_player(callback: types.CallbackQuery, state: FSMContext):
    # Голосование за игрока днем
    target_id = int(callback.data.split(":")[1])
    
    with Session() as session:
        player = session.query(Player).filter_by(user_id=callback.from_user.id).first()
        if not player or not player.alive:
            await callback.answer("Вы не можете голосовать!")
            return
        
        player.vote_target = target_id
        session.commit()
        
        target = session.query(Player).filter_by(user_id=target_id).first()
        await callback.answer(f"✅ Вы проголосовали за {target.name}") 