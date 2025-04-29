from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    state = Column(String)  # waiting, night, discussion, day, ended
    current_phase = Column(String)
    
    players = relationship("Player", back_populates="game")

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String)
    role = Column(String)  # mafia, detective, doctor, civilian
    alive = Column(Boolean, default=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    
    game = relationship("Game", back_populates="players")

# Создаем таблицы
Base.metadata.create_all(engine)