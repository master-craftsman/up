#!/bin/bash

# Скрипт для установки aiogram 3.x и зависимостей на macOS

echo "Проверка наличия Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "Homebrew не установлен. Рекомендуется установить Homebrew для управления пакетами."
    echo "Вы можете установить его с помощью команды:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo "После установки Homebrew запустите скрипт снова."
    exit 1
fi

echo "Проверка наличия Python..."
if ! command -v python3 &> /dev/null; then
    echo "Установка Python..."
    brew install python
fi

echo "Проверка наличия Rust (необходим для некоторых зависимостей aiogram 3.x)..."
if ! command -v rustc &> /dev/null; then
    echo "Установка Rust..."
    brew install rust
fi

echo "Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

echo "Обновление pip..."
pip install --upgrade pip

echo "Установка зависимостей..."
pip install requests
pip install python-dotenv

# Установка aiogram 3.x
echo "Установка aiogram 3.x..."
pip install aiogram

echo "Проверка установленных пакетов..."
pip list | grep -E 'aiogram|requests|python-dotenv'

echo "Установка завершена!"
echo "Теперь вы можете запустить бота командой: python bot_telegram_v3.py"
echo "Не забудьте создать файл .env с вашим токеном бота и ID администраторов!"