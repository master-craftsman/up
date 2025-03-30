import logging
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from bot.database.db import add_user, log_action
from bot.config.config import is_admin
from bot.utils.keyboards import get_start_keyboard, get_admin_keyboard, get_gifts_keyboard

logger = logging.getLogger(__name__)

# Обработчик команды /start
async def cmd_start(message: Message):
    user_id = message.from_user.id
    add_user(user_id)
    log_action("start", user_id)
    
    # Выбираем клавиатуру в зависимости от статуса пользователя
    if is_admin(user_id):
        keyboard = get_admin_keyboard()
    else:
        keyboard = get_start_keyboard()
    
    await message.answer(
        "Привет!\nСпасибо за подписку 🤍\n\nЛюбой из подарков вы можете забрать по кнопке ниже БЕСПЛАТНО 👇",
        reply_markup=keyboard
    )

# Обработчик нажатия на кнопку "Выбрать подарок"
async def process_guide_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    log_action("get_guide", user_id)
    
    keyboard = get_gifts_keyboard()
    
    await callback.message.edit_text(
        "Привет!\nСпасибо за подписку 🤍\n\nЛюбой из подарков вы можете забрать по кнопке ниже БЕСПЛАТНО 👇", 
        reply_markup=keyboard
    )
    await callback.answer()

# Обработчик кнопки возврата в главное меню
async def process_back_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if is_admin(user_id):
        keyboard = get_admin_keyboard()
    else:
        keyboard = get_start_keyboard()
    
    await callback.message.edit_text(
        "Привет!\nСпасибо за подписку 🤍\n\nЛюбой из подарков вы можете забрать по кнопке ниже БЕСПЛАТНО 👇",
        reply_markup=keyboard
    )
    await callback.answer()