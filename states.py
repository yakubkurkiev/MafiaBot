from aiogram.fsm.state import State, StatesGroup

class GameStates(StatesGroup):
    WAITING = State()
    NIGHT = State()
    DISCUSSION = State()
    DAY = State()
    ENDED = State()