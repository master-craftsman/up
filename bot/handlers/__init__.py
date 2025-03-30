from aiogram import Router, F
from aiogram.filters import Command, CommandStart

from bot.handlers.user import cmd_start, process_guide_button, process_back_button
from bot.handlers.admin import (
    process_statistics_button, cmd_broadcast, handle_broadcast_button, 
    cancel_broadcast, process_broadcast_text, process_broadcast_photo, 
    process_broadcast_video, process_broadcast_forwarded, confirm_media_group,
    confirm_broadcast_handler, BroadcastStates
)

# Создаем роутеры для разных типов обработчиков
user_router = Router()
admin_router = Router()
broadcast_router = Router()

# Регистрируем обработчики пользовательских команд
user_router.message.register(cmd_start, CommandStart())
user_router.callback_query.register(process_guide_button, F.data == "get_guide")
user_router.callback_query.register(process_back_button, F.data == "back_to_main")

# Регистрируем обработчики админских команд
admin_router.callback_query.register(process_statistics_button, F.data == "statistics")
admin_router.message.register(cmd_broadcast, Command("broadcast"))
admin_router.callback_query.register(handle_broadcast_button, F.data == "broadcast")
admin_router.callback_query.register(cancel_broadcast, F.data == "cancel_broadcast")

# Регистрируем обработчики для рассылки
broadcast_router.message.register(process_broadcast_text, BroadcastStates.waiting_for_content, F.text)
broadcast_router.message.register(process_broadcast_photo, BroadcastStates.waiting_for_content, F.photo)
broadcast_router.message.register(process_broadcast_video, BroadcastStates.waiting_for_content, F.video)
broadcast_router.message.register(process_broadcast_forwarded, BroadcastStates.waiting_for_content)
broadcast_router.message.register(confirm_media_group, Command("confirm_media_group"))
broadcast_router.callback_query.register(confirm_broadcast_handler, F.data == "confirm_broadcast")

# Функция для настройки всех роутеров
def setup_routers(dp):
    # Подключаем роутеры к диспетчеру
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(broadcast_router)