from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Game, Player
from config import DB_PATH

# Создание движка и сессии
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

def init_db():
    """Инициализация базы данных (создание таблиц)"""
    Base.metadata.create_all(engine)

def get_game_by_chat_id(chat_id: int) -> Game:
    """Получить игру по ID чата"""
    session = Session()
    game = session.query(Game).filter_by(chat_id=chat_id).first()
    session.close()
    return game

def create_game(chat_id: int) -> Game:
    """Создать новую игру"""
    session = Session()
    game = Game(chat_id=chat_id)
    session.add(game)
    session.commit()
    session.refresh(game)
    session.close()
    return game

def add_player(game_id: int, user_id: int, username: str) -> Player:
    """Добавить игрока в игру"""
    session = Session()
    player = Player(game_id=game_id, user_id=user_id, username=username)
    session.add(player)
    session.commit()
    session.refresh(player)
    session.close()
    return player

def get_players_in_game(game_id: int) -> list[Player]:
    """Получить всех игроков в игре"""
    session = Session()
    players = session.query(Player).filter_by(game_id=game_id).all()
    session.close()
    return players

def update_player_role(player_id: int, role: str) -> None:
    """Обновить роль игрока"""
    session = Session()
    player = session.query(Player).filter_by(id=player_id).first()
    if player:
        player.role = role
        session.commit()
    session.close()