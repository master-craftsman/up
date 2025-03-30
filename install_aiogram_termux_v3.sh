#!/data/data/com.termux/files/usr/bin/bash

# Скрипт для установки aiogram 3.x и зависимостей в Termux без компиляции

echo "Обновление пакетов Termux..."
pkg update -y && pkg upgrade -y

echo "Установка необходимых пакетов..."
pkg install -y python openssl libffi clang

echo "Создание виртуального окружения..."
python -m venv venv
source venv/bin/activate

echo "Обновление pip..."
pip install --upgrade pip

echo "Установка зависимостей без компиляции..."
pip install --only-binary :all: requests
pip install --only-binary :all: python-dotenv

# Установка aiogram 3.x с минимальными зависимостями
echo "Установка aiogram 3.x..."
# Сначала устанавливаем необходимые зависимости
pip install --only-binary :all: certifi idna multidict yarl
pip install --only-binary :all: aiohttp
pip install --only-binary :all: pydantic

# Затем устанавливаем aiogram
pip install aiogram --no-deps

# Устанавливаем недостающие зависимости
pip install --only-binary :all: magic-filter

echo "Проверка установленных пакетов..."
pip list | grep -E 'aiogram|requests|python-dotenv|aiohttp|pydantic|magic-filter'

echo "Установка завершена!"
echo "Теперь вы можете запустить бота командой: python bot_telegram_v3.py"
echo "Не забудьте создать файл .env с вашим токеном бота и ID администраторов!"