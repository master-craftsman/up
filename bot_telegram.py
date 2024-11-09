import os
from dotenv import load_dotenv
import json
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters as ext_filters

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_IDS = json.loads(os.getenv('ADMIN_IDS', '[]'))

if not API_TOKEN:
    raise ValueError("Не задан токен бота. Установите переменную окружения TELEGRAM_BOT_TOKEN.")
if not ADMIN_IDS:
    logging.warning("Список админов пуст. Установите переменную окружения ADMIN_IDS.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

waiting_for_broadcast_content = False

def connect_db():
    return sqlite3.connect("users.db")

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

def add_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users')
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]

# Функция для команды /start
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("Выбрать подарок", callback_data='get_guide')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user_id = update.message.chat_id
    add_user(user_id)  
    await update.message.reply_text(
        "Привет!\nСпасибо за подписку 🤍\n\nЛюбой из подарков вы можете забрать по кнопке ниже БЕСПЛАТНО 👇",
        reply_markup=reply_markup
    )

# Функция для обработки нажатия на кнопку "Получить гайд"
async def handle_guide_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие на кнопку
    keyboard = [
        [InlineKeyboardButton("12 самых типичных ошибок русскоговорящих в английском", url="https://discovered-bassoon-2bf.notion.site/12-08637e6a6b0b4e0696e3ca5f2892f553?pvs=4")],
        [InlineKeyboardButton("120+ сокращений в английском языке", url="https://drive.google.com/file/d/1PG3L2hmUnyuvoOQ9SC0E5IDfSz6oa_QW/view?usp=sharing")],
        [InlineKeyboardButton("Ресурсы и приложения для прокачки английского", url="https://discovered-bassoon-2bf.notion.site/cbef9b46bd094bc183a8afbdc937bf4b?pvs=4")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Привет!\nСпасибо за подписку 🤍\n\nЛюбой из подарков вы можете забрать по кнопке ниже БЕСПЛАТНО 👇", reply_markup=reply_markup)

# Команда /broadcast
async def admin_broadcast(update: Update, context: CallbackContext) -> None:
    logger.info("Команда /broadcast вызвана.")
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    global waiting_for_broadcast_content
    waiting_for_broadcast_content = True
    context.user_data.clear()  # Очищаем данные перед новой рассылкой
    await update.message.reply_text("Пожалуйста, укажите текст и/или отправьте медиа для рассылки. После этого используйте /send_broadcast для запуска рассылки.")

# Команда /send_broadcast для выполнения рассылки
async def send_broadcast(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    await execute_broadcast(context)
    await update.message.reply_text("Рассылка завершена.")
    context.user_data.clear()  # Очищаем данные после отправки

async def execute_broadcast(context: CallbackContext) -> None:
    user_ids = get_all_users()
    
    # Получаем текст и медиа из user_data
    messages_to_send = context.user_data.get('messages_to_send', [])

    for user_id in user_ids:
        for message in messages_to_send:
            media = message.get('media', [])
            text = message.get('text', '')

            try:
                # Отправка медиа и текста
                if media:
                    for media_item in media:
                        media_type = media_item.get('type')
                        media_file_id = media_item.get('file_id')
                        if media_type == 'photo':
                            await context.bot.send_photo(chat_id=user_id, photo=media_file_id, caption=text or "")
                        elif media_type == 'video':
                            await context.bot.send_video(chat_id=user_id, video=media_file_id, caption=text or "")
                elif text:
                    await context.bot.send_message(chat_id=user_id, text=text)
                
                logger.info(f"Сообщение отправлено пользователю {user_id}")
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    logger.info("Рассылка завершена.")

# Функция для обработки текста
async def handle_broadcast_text(update: Update, context: CallbackContext) -> None:
    global waiting_for_broadcast_content
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS or not waiting_for_broadcast_content:
        return

    # Сохраняем текст для рассылки
    context.user_data.setdefault('messages_to_send', []).append({'text': update.message.text, 'media': []})
    await update.message.reply_text("Текст для рассылки сохранен. Отправьте медиа, если нужно, или используйте /send_broadcast для отправки.")

# Функция для обработки медиа с проверкой на наличие текста
async def handle_broadcast_media(update: Update, context: CallbackContext) -> None:
    global waiting_for_broadcast_content
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS or not waiting_for_broadcast_content:
        return

    # Проверяем, есть ли текст в сообщении с медиа
    caption = update.message.caption
    media_type = None
    media_file_id = None

    if update.message.photo:
        media_file_id = update.message.photo[-1].file_id
        media_type = 'photo'
    elif update.message.video:
        media_file_id = update.message.video.file_id
        media_type = 'video'
    
    # Сохраняем медиа в списке сообщений для рассылки
    if media_file_id and media_type:
        last_message = context.user_data.setdefault('messages_to_send', []).append({
            'text': caption or '',
            'media': [{'file_id': media_file_id, 'type': media_type}]
        })

    await update.message.reply_text("Медиа и текст для рассылки сохранены. Используйте /send_broadcast для отправки.")

# Регистрация команд и обработчиков
application = Application.builder().token(API_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_guide_button, pattern='get_guide'))  # Обработчик нажатий на кнопку
application.add_handler(CommandHandler("broadcast", admin_broadcast))
application.add_handler(CommandHandler("send_broadcast", send_broadcast))
application.add_handler(MessageHandler(ext_filters.TEXT & ext_filters.User(user_id=ADMIN_IDS), handle_broadcast_text))
application.add_handler(MessageHandler(ext_filters.PHOTO | ext_filters.VIDEO & ext_filters.User(user_id=ADMIN_IDS), handle_broadcast_media))

if __name__ == "__main__":
    create_table()
    application.run_polling()