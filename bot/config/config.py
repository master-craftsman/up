import os
import json
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_IDS = json.loads(os.getenv('ADMIN_IDS', '[]'))

if not API_TOKEN:
    raise ValueError("Не задан токен бота. Установите переменную окружения TELEGRAM_BOT_TOKEN.")
if not ADMIN_IDS:
    logging.warning("Список админов пуст. Установите переменную окружения ADMIN_IDS.")

# Преобразуем строковые ID в целые числа
ADMIN_IDS = [int(admin_id) for admin_id in ADMIN_IDS]

# Настройка логирования
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("bot_debug.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Функция для проверки, является ли пользователь администратором
def is_admin(user_id):
    return user_id in ADMIN_IDS