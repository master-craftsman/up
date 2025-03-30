import re
import logging
import asyncio
from aiogram import F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio

from bot.database.db import log_action, get_statistics, get_all_users
from bot.config.config import is_admin
from bot.utils.keyboards import get_back_keyboard, get_broadcast_confirmation_keyboard, get_cancel_broadcast_keyboard

logger = logging.getLogger(__name__)

# Состояния для FSM
class BroadcastStates(StatesGroup):
    waiting_for_content = State()
    waiting_for_confirmation = State()

# Обработчик нажатия на кнопку "Статистика"
async def process_statistics_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if not is_admin(user_id):
        await callback.answer("У вас нет прав для просмотра статистики.")
        return
    
    stats = get_statistics()
    
    stats_text = (
        "📊 **Статистика бота** 📊\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"👤 Активных за 7 дней: {stats['active_users']}\n"
        f"🚀 Использований /start: {stats['start_count']}\n"
        f"🎁 Нажатий на 'Выбрать подарок': {stats['guide_clicks']}\n"
        f"📨 Количество рассылок: {stats['broadcast_count']}\n"
    )
    
    # Добавляем кнопку возврата
    keyboard = get_back_keyboard()
    
    await callback.message.edit_text(stats_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

# Обработчик команды /broadcast для начала рассылки
async def cmd_broadcast(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
        
    await state.set_state(BroadcastStates.waiting_for_content)
    await message.answer("Отправьте сообщение для рассылки:")

# Обработчик кнопки рассылки
async def handle_broadcast_button(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    await state.set_state(BroadcastStates.waiting_for_content)
    log_action("broadcast_init", user_id)
    
    # Создаем клавиатуру с кнопкой отмены
    keyboard = get_cancel_broadcast_keyboard()
    
    await callback.message.answer(
        "Пожалуйста, отправьте сообщение для рассылки.\n\n"
        "Вы можете:\n"
        "- Отправить текст (поддерживается форматирование Markdown)\n"
        "- Отправить медиа (фото, видео) с подписью\n"
        "- Отправить несколько медиа в одном сообщении (медиа-группа)\n"
        "- Переслать сообщение из другого чата\n\n"
        "После отправки контента, вам будет предложено подтвердить рассылку.\n"
        "Для медиа-групп используйте команду /confirm_media_group после отправки всех медиа.",
        reply_markup=keyboard
    )

# Обработчик отмены рассылки
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
    await callback.message.edit_text("Рассылка отменена.")
    await callback.answer()

# Функция для создания предпросмотра текстового сообщения
def create_text_preview(text, is_command=False):
    # Если это команда /confirm_media_group, показываем специальное сообщение
    if is_command and text.strip().startswith('/confirm_media_group'):
        return "Команда подтверждения медиа-группы. Будет использована для подтверждения отправки медиа-группы."
    return text

# Обработчик для получения контента рассылки (текст)
async def process_broadcast_text(message: Message, state: FSMContext):
    # Сохраняем текст сообщения
    original_text = message.text
    cleaned_text = original_text.rstrip('/')
    
    # Проверяем, является ли это командой /confirm_media_group
    is_confirm_command = original_text.strip().startswith('/confirm_media_group')
    
    # Если это команда /confirm_media_group, не меняем тип сообщения
    # Это позволит сохранить тип media_group, если он был установлен ранее
    if is_confirm_command:
        # Получаем текущие данные состояния
        data = await state.get_data()
        # Сохраняем только текст и entities, не трогая message_type
        await state.update_data(message_text=cleaned_text, entities=message.entities)
    else:
        # Для обычного текста устанавливаем тип сообщения как text
        await state.update_data(message_text=cleaned_text, entities=message.entities, message_type="text")
    
    await state.set_state(BroadcastStates.waiting_for_confirmation)
    
    # Создаем клавиатуру для подтверждения
    keyboard = get_broadcast_confirmation_keyboard()
    
    # Создаем предпросмотр с учетом типа сообщения
    preview_text = create_text_preview(original_text, is_confirm_command)
    
    await message.answer(
        f"Предпросмотр сообщения для рассылки:\n\n{preview_text}\n\n"
        "Подтвердите отправку:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Вспомогательная функция для обработки медиа в группе
async def _process_media_in_group(message: Message, state: FSMContext, media_type: str, media_id: str):
    # Получаем текущие данные состояния
    data = await state.get_data()
    media_group = data.get('media_group', [])
    media_group_id = data.get('media_group_id')
    
    # Если это новая медиа-группа или продолжение текущей
    if not media_group_id or media_group_id != message.media_group_id:
        media_group = []
        media_group_id = message.media_group_id
    
    # Добавляем медиа в группу
    caption = message.caption or ""
    media_group.append({
        'type': media_type,
        'media': media_id,
        'caption': caption if not data.get('caption') else "",
        'caption_entities': message.caption_entities if not data.get('caption_entities') else None
    })
    
    # Сохраняем обновленную медиа-группу
    await state.update_data(
        media_group=media_group,
        media_group_id=media_group_id,
        caption=caption or data.get('caption', ""),
        caption_entities=message.caption_entities or data.get('caption_entities'),
        message_type="media_group"
    )
    
    # Информируем пользователя
    await message.answer(f"Медиа добавлено в группу. Всего медиа в группе: {len(media_group)}. Отправьте все медиа, затем подтвердите отправку.")

# Обработчик для получения контента рассылки (фото)
async def process_broadcast_photo(message: Message, state: FSMContext):
    # Проверяем, является ли это частью медиа-группы
    if message.media_group_id:
        photo_id = message.photo[-1].file_id
        await _process_media_in_group(message, state, 'photo', photo_id)
    else:
        # Обычное одиночное фото
        photo_id = message.photo[-1].file_id
        caption = message.caption or ""
        
        await state.update_data(
            photo_id=photo_id, 
            caption=caption, 
            caption_entities=message.caption_entities,  # Сохраняем entities подписи
            message_type="photo"
        )
        await state.set_state(BroadcastStates.waiting_for_confirmation)
        
        # Создаем клавиатуру для подтверждения
        keyboard = get_broadcast_confirmation_keyboard()
        
        await message.answer(
            "Предпросмотр фото для рассылки (выше) с подписью:\n\n"
            f"{caption}\n\n"
            "Подтвердите отправку:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

# Обработчик для получения контента рассылки (видео)
async def process_broadcast_video(message: Message, state: FSMContext):
    # Проверяем, является ли это частью медиа-группы
    if message.media_group_id:
        video_id = message.video.file_id
        await _process_media_in_group(message, state, 'video', video_id)
    else:
        # Обычное одиночное видео
        video_id = message.video.file_id
        caption = message.caption or ""
        
        await state.update_data(
            video_id=video_id, 
            caption=caption, 
            caption_entities=message.caption_entities,
            message_type="video"
        )
        await state.set_state(BroadcastStates.waiting_for_confirmation)
        
        # Создаем клавиатуру для подтверждения
        keyboard = get_broadcast_confirmation_keyboard()
        
        await message.answer(
            "Предпросмотр видео для рассылки (выше) с подписью:\n\n"
            f"{caption}\n\n"
            "Подтвердите отправку:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

# Обработчик для получения контента рассылки (пересылаемое сообщение)
async def process_broadcast_forwarded(message: Message, state: FSMContext):
    # Проверяем, является ли сообщение пересланным
    if message.forward_from or message.forward_from_chat:
        # Сохраняем информацию о пересланном сообщении
        await state.update_data(
            from_chat_id=message.forward_from_chat.id if message.forward_from_chat else message.forward_from.id,
            message_id=message.message_id,
            message_type="forwarded"
        )
        await state.set_state(BroadcastStates.waiting_for_confirmation)
        
        # Создаем клавиатуру для подтверждения
        keyboard = get_broadcast_confirmation_keyboard()
        
        await message.answer(
            "Предпросмотр пересланного сообщения для рассылки (выше).\n\n"
            "Подтвердите отправку:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

# Функция для очистки команды /confirm_media_group из текста
def clean_confirm_media_group_command(text):
    if not text:
        return ""
    # Удаляем команду в любом месте текста
    cleaned_text = re.sub(r'/confirm_media_group\b', '', text).strip()
    return cleaned_text

# Функция для создания предпросмотра медиа-группы
def create_media_group_preview(media_group, caption):
    # Очищаем подпись от команды
    if caption:
        caption = clean_confirm_media_group_command(caption)
    
    # Формируем детальное описание содержимого медиа-группы
    preview_text = f"Предпросмотр медиа-группы для рассылки:\n\n"
    preview_text += f"📷 Медиа-группа содержит {len(media_group)} элементов.\n"
    
    # Добавляем информацию о типах медиа в группе
    media_types = {}
    for item in media_group:
        media_type = item['type']
        media_types[media_type] = media_types.get(media_type, 0) + 1
    
    for media_type, count in media_types.items():
        if media_type == 'photo':
            preview_text += f"🖼 Фото: {count}\n"
        elif media_type == 'video':
            preview_text += f"🎬 Видео: {count}\n"
        elif media_type == 'document':
            preview_text += f"📄 Документы: {count}\n"
        elif media_type == 'audio':
            preview_text += f"🎵 Аудио: {count}\n"
    
    # Добавляем подписи из элементов медиа-группы
    captions = []
    for item in media_group:
        item_caption = item.get('caption', '')
        if item_caption:
            item_caption = clean_confirm_media_group_command(item_caption)
            if item_caption and item_caption not in captions:
                captions.append(item_caption)
    
    # Добавляем общую подпись, если она есть
    if caption and caption not in captions:
        preview_text += f"\n📝 Общая подпись: {caption}\n"
    
    # Добавляем подписи из элементов, если они отличаются от общей
    if captions:
        for i, item_caption in enumerate(captions):
            if item_caption != caption:
                preview_text += f"\n📝 Подпись {i+1}: {item_caption}\n"
    
    return preview_text

# Обработчик подтверждения медиа-группы
async def confirm_media_group(message: Message, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    media_group = data.get('media_group', [])
    
    if not media_group:
        await message.answer("Медиа-группа пуста. Сначала отправьте медиа-файлы.")
        return
    
    # Сохраняем текст команды для последующей обработки
    command_text = message.text if message.text else ""
    
    # Сохраняем тип сообщения как media_group и сохраняем текст команды
    # Важно: сохраняем message_type как media_group
    await state.update_data(
        message_type="media_group", 
        message_text=command_text,
        entities=message.entities
    )
    await state.set_state(BroadcastStates.waiting_for_confirmation)
    
    # Создаем клавиатуру для подтверждения
    keyboard = get_broadcast_confirmation_keyboard()
    
    # Получаем подпись
    caption = data.get('caption', '')
    
    # Создаем предпросмотр медиа-группы
    preview_text = create_media_group_preview(media_group, caption)
    preview_text += "\nПодтвердите отправку:"
    
    await message.answer(
        preview_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Функция для отправки текстового сообщения
async def send_text_message(bot: Bot, recipient_id: int, broadcast_data: dict):
    logger.debug(f"Отправка текстового сообщения пользователю {recipient_id}")
    # Проверяем, не является ли текст командой /confirm_media_group
    message_text = broadcast_data.get("message_text", "")
    if message_text and message_text.strip().startswith('/confirm_media_group'):
        # Удаляем команду из текста
        message_text = clean_confirm_media_group_command(message_text)
        logger.debug(f"Текст после удаления команды: '{message_text}'")
    
    # Отправляем только если текст не пустой после очистки
    if message_text:
        await bot.send_message(
            chat_id=recipient_id,
            text=message_text,
            entities=broadcast_data.get('entities'),
            disable_web_page_preview=True
        )
        logger.debug(f"Текстовое сообщение успешно отправлено пользователю {recipient_id}")
        return True
    else:
        logger.debug(f"Пропускаем отправку пустого текстового сообщения пользователю {recipient_id}")
        return False

# Функция для отправки фото
async def send_photo_message(bot: Bot, recipient_id: int, broadcast_data: dict):
    logger.debug(f"Отправка фото пользователю {recipient_id}")
    await bot.send_photo(
        chat_id=recipient_id,
        photo=broadcast_data["photo_id"],
        caption=broadcast_data.get("caption", ""),
        caption_entities=broadcast_data.get('caption_entities')
    )
    logger.debug(f"Фото успешно отправлено пользователю {recipient_id}")
    return True

# Функция для отправки видео
async def send_video_message(bot: Bot, recipient_id: int, broadcast_data: dict):
    logger.debug(f"Отправка видео пользователю {recipient_id}")
    await bot.send_video(
        chat_id=recipient_id,
        video=broadcast_data["video_id"],
        caption=broadcast_data.get("caption", ""),
        caption_entities=broadcast_data.get('caption_entities')
    )
    logger.debug(f"Видео успешно отправлено пользователю {recipient_id}")
    return True

# Функция для выполнения рассылки
async def perform_broadcast(bot: Bot, user_ids: list, broadcast_data: dict, message_type: str = None) -> tuple:
    # Если message_type не передан, берем его из broadcast_data
    if message_type is None:
        message_type = broadcast_data.get('message_type', 'text')
    
    logger.debug(f"Начинаем рассылку для {len(user_ids)} пользователей. Тип сообщения: {message_type}")
    successful = 0
    failed = 0
    
    # Для медиа-групп используем параллельную отправку
    if message_type == 'media_group':
        try:
            media_group = broadcast_data.get('media_group', [])
            if not media_group:
                logger.warning("Пустая медиа-группа для рассылки")
                return 0, len(user_ids)
            
            # Подготавливаем медиа-группу для отправки
            input_media = []
            for item in media_group:
                if item['type'] == 'photo':
                    media = InputMediaPhoto(media=item['media'])
                elif item['type'] == 'video':
                    media = InputMediaVideo(media=item['media'])
                elif item['type'] == 'document':
                    media = InputMediaDocument(media=item['media'])
                elif item['type'] == 'audio':
                    media = InputMediaAudio(media=item['media'])
                else:
                    continue
                
                # Добавляем подпись только к первому элементу
                if len(input_media) == 0 and broadcast_data.get('caption'):
                    media.caption = broadcast_data.get('caption')
                    media.caption_entities = broadcast_data.get('caption_entities')
                
                input_media.append(media)
            
            # Отправляем медиа-группу всем пользователям
            tasks = []
            for user_id in user_ids:
                tasks.append(bot.send_media_group(chat_id=user_id, media=input_media))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = sum(1 for res in results if not isinstance(res, Exception))
            failed = len(results) - successful
        except Exception as e:
            logger.error(f"Ошибка при отправке медиа-группы: {e}")
            return 0, len(user_ids)
    else:
        # Для остальных типов сообщений используем последовательную отправку
        for user_id in user_ids:
            try:
                # Выбираем функцию отправки в зависимости от типа сообщения
                if message_type == "text":
                    result = await send_text_message(bot, user_id, broadcast_data)
                elif message_type == "photo":
                    result = await send_photo_message(bot, user_id, broadcast_data)
                elif message_type == "video":
                    result = await send_video_message(bot, user_id, broadcast_data)
                elif message_type == "media_group":
                    result = await send_media_group_message(bot, user_id, broadcast_data)
                elif message_type == "forwarded":
                    # Для пересланных сообщений
                    result = await bot.forward_message(
                        chat_id=user_id,
                        from_chat_id=broadcast_data["from_chat_id"],
                        message_id=broadcast_data["message_id"]
                    )
                    result = True if result else False
                else:
                    logger.warning(f"Неизвестный тип сообщения: {message_type}")
                    result = False
                
                # Увеличиваем счетчики успешных/неуспешных отправок
                if result:
                    successful += 1
                else:
                    failed += 1
                    
                # Небольшая задержка между отправками, чтобы избежать ограничений API
                await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
                failed += 1
    
    logger.debug(f"Рассылка завершена. Успешно: {successful}, с ошибками: {failed}")
    return successful, failed

# Обработчик подтверждения рассылки
async def confirm_broadcast_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    logger.debug(f"Вызвана функция confirm_broadcast пользователем {user_id}")
    
    # Получаем данные из состояния
    broadcast_data = await state.get_data()
    message_type = broadcast_data.get("message_type")
    logger.debug(f"Тип сообщения для рассылки: {message_type}")
    logger.debug(f"Данные для рассылки: {broadcast_data}")
    
    # Получаем список всех пользователей
    user_ids = get_all_users()
    logger.debug(f"Количество пользователей для рассылки: {len(user_ids)}")

    # Проверяем, если у нас есть media_group в данных, то всегда устанавливаем тип сообщения как media_group
    # независимо от текущего значения message_type
    if broadcast_data.get('media_group'):
        message_type = 'media_group'
        # Обновляем данные состояния с правильным типом сообщения
        await state.update_data(message_type='media_group')
        broadcast_data['message_type'] = 'media_group'
        logger.debug(f"Установлен тип сообщения: {message_type}")
    
    successful, failed = await perform_broadcast(bot, user_ids, broadcast_data, message_type)
    
    # Логируем действие
    log_action("broadcast", user_id)
    logger.debug(f"Рассылка завершена. Успешно: {successful}, с ошибками: {failed}")
    
    # Отправляем отчет о рассылке
    try:
        # Редактируем сообщение с результатами рассылки
        logger.debug("Отправляем отчет о результатах рассылки")
        await callback.message.edit_text(
            f"Рассылка завершена.\n\n"
            f"✅ Успешно отправлено: {successful}\n"
            f"❌ Ошибки при отправке: {failed}\n")
    except Exception as e:
        logger.error(f"Не удалось отправить отчет о результатах рассылки: {e}")
        logger.debug(f"Детали ошибки: {str(e)}")
    
    # Очищаем состояние
    await state.clear()

# Функция для отправки медиа-группы одному пользователю
async def send_media_group_to_user(bot: Bot, recipient_id: int, broadcast_data: dict):
    message_type = broadcast_data.get('message_type')
    
    if message_type == 'media_group':
        return await send_media_group_message(bot, recipient_id, broadcast_data)
    elif message_type == 'text':
        text = clean_confirm_media_group_command(broadcast_data.get('caption', ''))
        if text:
            await bot.send_message(chat_id=recipient_id, text=text, entities=broadcast_data.get('caption_entities'))
            return True
        return False

# Функция для подготовки и отправки медиа-группы
async def send_media_group_message(bot: Bot, recipient_id: int, broadcast_data: dict):
    logger.debug(f"Отправка медиа-группы пользователю {recipient_id}")
    # Отправляем группу медиа
    media_group = broadcast_data.get('media_group', [])
    logger.debug(f"Медиа-группа содержит {len(media_group)} элементов")
    
    if not media_group:
        logger.warning(f"Пустая медиа-группа для пользователя {recipient_id}")
        return False
    
    input_media = []
    has_caption_added = False
    caption = broadcast_data.get('caption', '')
    
    # Подготавливаем медиа для отправки
    for item in media_group:
        if item['type'] == 'photo':
            media = InputMediaPhoto(media=item['media'])
        elif item['type'] == 'video':
            media = InputMediaVideo(media=item['media'])
        elif item['type'] == 'document':
            media = InputMediaDocument(media=item['media'])
        elif item['type'] == 'audio':
            media = InputMediaAudio(media=item['media'])
        else:
            continue
        
        # Добавляем подпись только к первому элементу
        if not has_caption_added and caption:
            media.caption = caption
            media.caption_entities = broadcast_data.get('caption_entities')
            has_caption_added = True
        
        input_media.append(media)
    
    # Отправляем медиа-группу
    try:
        await bot.send_media_group(chat_id=recipient_id, media=input_media)
        logger.debug(f"Медиа-группа успешно отправлена пользователю {recipient_id}")
        
        # Если есть подпись, но она не была добавлена к медиа, отправляем отдельным сообщением
        if caption and not has_caption_added:
            logger.debug(f"Отправляем отдельное текстовое сообщение с подписью пользователю {recipient_id}")
            await bot.send_message(
                chat_id=recipient_id,
                text=caption,
                entities=broadcast_data.get('caption_entities')
            )
            logger.debug(f"Текстовое сообщение с подписью успешно отправлено пользователю {recipient_id}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке медиа-группы пользователю {recipient_id}: {e}")
        return False

# Функция для пересылки сообщения
async def send_forwarded_message(bot: Bot, recipient_id: int, broadcast_data: dict):
    logger.debug(f"Пересылка сообщения пользователю {recipient_id}")
    # Используем copy_message вместо forward_message для сохранения форматирования
    await bot.copy_message(
        chat_id=recipient_id,
        from_chat_id=broadcast_data["from_chat_id"],
        message_id=broadcast_data["message_id"]
    )
    
    # Выполняем рассылку
    result = await perform_broadcast(bot, user_ids, broadcast_data)
    if isinstance(result, tuple) and len(result) == 2:
        successful, failed = result
    else:
        successful = 0
        failed = len(user_ids)
    
    # Логируем действие
    log_action("broadcast", user_id)
    logger.debug(f"Рассылка завершена. Успешно: {successful}, с ошибками: {failed}")
    
    # Отправляем отчет о рассылке
    try:
        # Редактируем сообщение с результатами рассылки
        logger.debug("Отправляем отчет о результатах рассылки")
        await callback.message.edit_text(
            f"Рассылка завершена.\n\n"
            f"✅ Успешно отправлено: {successful}\n"
            f"❌ Ошибки при отправке: {failed}\n")
    except Exception as e:
        logger.error(f"Не удалось отправить отчет о результатах рассылки: {e}")
        logger.debug(f"Детали ошибки: {str(e)}")