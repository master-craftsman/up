import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config.config import API_TOKEN, setup_logging
from bot.database.db import create_table
from bot.handlers import setup_routers

# Настройка логирования
logger = setup_logging()

async def main():
    # Создаем таблицы в базе данных, если они не существуют
    create_table()
    
    # Создаем экземпляры бота и диспетчера
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрируем все роутеры
    setup_routers(dp)
    
    # Запускаем бота
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())