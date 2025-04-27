from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Game(Base):
    """Модель игры"""
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)  # ID чата, где проходит игра
    is_active = Column(Boolean, default=False)  # Активна ли игра
    day_number = Column(Integer, default=1)    # Номер дня
    
    # Связь с игроками
    players = relationship("Player", back_populates="game")

class Player(Base):
    """Модель игрока"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)      # ID пользователя
    username = Column(String)      # Имя пользователя
    role = Column(String)          # Роль (mafia, doctor, detective, civilian)
    is_alive = Column(Boolean, default=True)  # Жив ли игрок
    game_id = Column(Integer, ForeignKey('games.id'))  # ID игры
    
    # Связь с игрой
    game = relationship("Game", back_populates="players")