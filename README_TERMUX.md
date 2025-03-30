# Инструкция по установке и запуску Telegram бота в Termux

## Подготовка

1. Установите Termux из [F-Droid](https://f-droid.org/packages/com.termux/) (рекомендуется) или Google Play Store
2. Запустите Termux и обновите пакеты:
   ```bash
   pkg update && pkg upgrade -y
   ```
3. Установите Git для клонирования репозитория:
   ```bash
   pkg install git -y
   ```

## Установка бота

1. Клонируйте репозиторий (или скопируйте файлы вручную):
   ```bash
   git clone https://your-repository-url.git
   cd your-repository-name
   ```

2. Сделайте скрипт установки исполняемым:
   ```bash
   chmod +x install_aiogram_termux.sh
   ```

3. Запустите скрипт установки:
   ```bash
   ./install_aiogram_termux.sh
   ```
   Скрипт установит Python, создаст виртуальное окружение и установит все необходимые зависимости без компиляции.

## Настройка бота

1. Создайте файл .env в корневой директории проекта:
   ```bash
   nano .env
   ```

2. Добавьте следующие строки в файл .env:
   ```
   TELEGRAM_BOT_TOKEN=ваш_токен_бота
   ADMIN_IDS=["ваш_id_в_телеграм"]
   ```
   Замените `ваш_токен_бота` на токен, полученный от @BotFather, и `ваш_id_в_телеграм` на ваш ID в Telegram.

3. Сохраните файл: нажмите Ctrl+O, затем Enter, затем Ctrl+X для выхода из редактора.

## Запуск бота

1. Активируйте виртуальное окружение (если оно еще не активировано):
   ```bash
   source venv/bin/activate
   ```

2. Запустите бота:
   ```bash
   python bot_telegram.py
   ```

## Советы по использованию в Termux

1. Для запуска бота в фоновом режиме используйте:
   ```bash
   nohup python bot_telegram.py > bot.log 2>&1 &
   ```
   Это позволит боту работать даже после закрытия приложения Termux.

2. Чтобы проверить, запущен ли бот, используйте:
   ```bash
   ps aux | grep python
   ```

3. Для остановки бота найдите его PID и выполните:
   ```bash
   kill PID
   ```
   где PID - идентификатор процесса из предыдущей команды.

4. Для просмотра логов:
   ```bash
   tail -f bot.log
   ```

## Решение проблем

1. **Ошибка при установке aiogram**: Если возникают проблемы с установкой aiogram, попробуйте установить более старую версию:
   ```bash
   pip install aiogram==2.20
   ```

2. **Проблемы с SSL**: Если возникают ошибки SSL, убедитесь, что установлен пакет openssl:
   ```bash
   pkg install openssl -y
   ```

3. **Ошибки импорта модулей**: Убедитесь, что все зависимости установлены правильно:
   ```bash
   pip install -r requirements.txt
   ```

4. **Termux засыпает**: Чтобы Termux не засыпал и бот продолжал работать, установите пакет termux-api и используйте wake-lock:
   ```bash
   pkg install termux-api -y
   termux-wake-lock
   ```
   Для отключения: `termux-wake-unlock`