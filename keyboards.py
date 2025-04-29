from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Session
from constants import ROLES

def get_join_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Присоединиться", callback_data="join_game")]
        ]
    )

def get_night_action_kb(game_id, action_type):
    with Session() as session:
        game = session.query(Game).filter_by(id=game_id).first()
        alive_players = [p for p in game.players if p.alive]
        
        buttons = []
        for player in alive_players:
            if player.role != action_type:  # Нельзя выбирать себя
                buttons.append(
                    [InlineKeyboardButton(
                        text=f"{player.name}",
                        callback_data=f"{action_type}_select:{player.user_id}"
                    )]
                )
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_voting_kb(game_id):
    with Session() as session:
        game = session.query(Game).filter_by(id=game_id).first()
        alive_players = [p for p in game.players if p.alive]
        
        buttons = [
            [InlineKeyboardButton(text=p.name, callback_data=f"vote:{p.user_id}")]
            for p in alive_players
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)