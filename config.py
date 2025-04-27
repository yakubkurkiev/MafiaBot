from pathlib import Path

# Путь к базе данных
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "database" / "mafia.db"

# Настройки бота
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Замените на реальный токен
ADMIN_IDS = [123456789]       # ID администраторов

# Настройки игры
ROLES = {
    "mafia": 2,      # Количество мафий
    "doctor": 1,     # Количество докторов
    "detective": 1,  # Количество детективов
    "civilian": 4    # Количество мирных жителей
}