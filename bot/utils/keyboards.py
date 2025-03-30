from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Создание клавиатуры для стартового сообщения
def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать подарок", callback_data="get_guide")]
    ])
    return keyboard

# Создание клавиатуры для админов
def get_admin_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать подарок", callback_data="get_guide")],
        [InlineKeyboardButton(text="Статистика", callback_data="statistics")],
        [InlineKeyboardButton(text="Рассылка", callback_data="broadcast")]
    ])
    return keyboard

# Клавиатура для подарков
def get_gifts_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="12 самых типичных ошибок русскоговорящих в английском", 
                             url="https://discovered-bassoon-2bf.notion.site/12-08637e6a6b0b4e0696e3ca5f2892f553?pvs=4")],
        [InlineKeyboardButton(text="120+ сокращений в английском языке", 
                             url="https://drive.google.com/file/d/1PG3L2hmUnyuvoOQ9SC0E5IDfSz6oa_QW/view?usp=sharing")],
        [InlineKeyboardButton(text="Ресурсы и приложения для прокачки английского", 
                             url="https://discovered-bassoon-2bf.notion.site/cbef9b46bd094bc183a8afbdc937bf4b?pvs=4")]
    ])
    return keyboard

# Клавиатура для подтверждения рассылки
def get_broadcast_confirmation_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_broadcast")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_broadcast")]
    ])
    return keyboard

# Клавиатура для отмены рассылки
def get_cancel_broadcast_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="cancel_broadcast")]
    ])
    return keyboard

# Клавиатура для возврата в главное меню
def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Назад", callback_data="back_to_main")]
    ])
    return keyboard