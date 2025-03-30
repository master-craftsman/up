#!/data/data/com.termux/files/usr/bin/bash

# Скрипт для установки aiogram и зависимостей в Termux без компиляции

echo "Обновление пакетов Termux..."
pkg update -y && pkg upgrade -y

echo "Установка необходимых пакетов..."
pkg install -y python openssl libffi

echo "Создание виртуального окружения..."
python -m venv venv
source venv/bin/activate

echo "Обновление pip..."
pip install --upgrade pip

echo "Установка зависимостей без компиляции..."
pip install --only-binary :all: requests
pip install --only-binary :all: python-dotenv

# Установка aiogram с указанием версии и без компиляции
echo "Установка aiogram..."
pip install --only-binary :all: aiogram==2.25.1

echo "Проверка установленных пакетов..."
pip list | grep -E 'aiogram|requests|python-dotenv'

echo "Установка завершена!"
echo "Теперь вы можете запустить бота командой: python bot_telegram.py"
echo "Не забудьте создать файл .env с вашим токеном бота и ID администраторов!"