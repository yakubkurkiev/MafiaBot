from aiogram.fsm.state import State, StatesGroup

class GameState(StatesGroup):
    """Состояния игры"""
    waiting_for_players = State()      # Ожидание игроков
    night = State()                   # Ночь (мафия и доктор делают выбор)
    day_discussion = State()          # Дневное обсуждение
    day_voting = State()              # Голосование днем
    game_end = State()                # Игра завершена