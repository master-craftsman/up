import os
import json
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters

# Получаем значения из переменных окружения
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_IDS = json.loads(os.getenv('ADMIN_IDS', '[]'))

# Проверка наличия токена
if not API_TOKEN:
    raise ValueError("Не задан токен бота. Установите переменную окружения TELEGRAM_BOT_TOKEN.")

# Проверка наличия админов
if not ADMIN_IDS:
    logging.warning("Список админов пуст. Установите переменную окружения ADMIN_IDS.")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для отслеживания состояния ожидания текста рассылки
waiting_for_broadcast_text = False

# Функция для подключения к базе данных
def connect_db():
    conn = sqlite3.connect("users.db")
    return conn

# Функция для создания таблицы пользователей (если она ещё не существует)
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

# Функция для добавления нового пользователя
def add_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

# Функция для получения списка всех пользователей
def get_all_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users')
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]

# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Получить гайд", callback_data='get_guide')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user_id = update.message.chat_id
    add_user(user_id)  # Добавляем пользователя в базу днных
    await update.message.reply_text(
        "Привет! Я бот для оплаты занятий по английскому. Чтобы получить бесплатный гайд, нажми на кнопку ниже!", reply_markup=reply_markup)

# Функция для обработки команды /get_guide
async def get_guide(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Скачать гайд", url="https://your-link-to-guide.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Check if this is a callback query (button press) or a direct command
    if update.callback_query:
        await update.callback_query.message.reply_text("Вот твой бесплатный гайд!", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Вот твой бесплатный гайд!", reply_markup=reply_markup)

# Добавьте новую функцию для обработки команды /broadcast
async def admin_broadcast(update: Update, context: CallbackContext) -> None:
    global waiting_for_broadcast_text
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    if context.args:
        message_text = ' '.join(context.args)
        await broadcast_message(context, message_text)
        await update.message.reply_text("Рассылка выполнена успешно.")
    else:
        waiting_for_broadcast_text = True
        await update.message.reply_text("Пожалуйста, отправьте текст для рассылки.")

async def handle_broadcast_text(update: Update, context: CallbackContext) -> None:
    global waiting_for_broadcast_text
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS or not waiting_for_broadcast_text:
        return

    message_text = update.message.text
    await broadcast_message(context, message_text)
    await update.message.reply_text("Рассылка выполнена успешно.")
    waiting_for_broadcast_text = False

# Измените функцию broadcast_message, чтобы она принимала текст сообщения:
async def broadcast_message(context: CallbackContext, message_text: str) -> None:
    users = get_all_users()
    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message_text,
#                reply_markup=InlineKeyboardMarkup(
#                    [[InlineKeyboardButton("Скачать гайд", url="https://your-link-to-guide.com")]]
 #               )
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

# Функция для обработки нажатий кнопок
async def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'get_guide':
        await get_guide(update, context)

# Основная функция для запуска бота
def main() -> None:
    # Создаем таблицу при первом запуске
    create_table()

    # Инициализация бота и диспетчера
    application = Application.builder().token(API_TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_guide", get_guide))
    application.add_handler(CallbackQueryHandler(button_callback))  # Добавляем обработчик для кнопок
    application.add_handler(CommandHandler("broadcast", admin_broadcast))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_text))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
