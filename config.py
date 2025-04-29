import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///mafia.db")

# Настройки игры
MAX_PLAYERS = 10  # Максимальное количество игроков
MIN_PLAYERS = 5   # Минимальное количество для старта
DISCUSSION_TIME = 50  # Время обсуждения в секундах
VOTING_TIME = 30      # Время голосования в секундах
NIGHT_TIME = 45       # Время на ночные действия