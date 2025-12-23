import telebot
from telebot.types import Message
import time
import threading
from datetime import datetime

# Импорт наших модулей
from config import Config
from database_manager import DatabaseManager
from utils import TagManager, UserValidator, SuggestionBuilder, MessageFormatter
from logger import logger

class SuggestBot:
    """Основной класс бота"""
    
    def __init__(self):
        # Валидация конфигурации
        Config.validate()
        
        # Инициализация компонентов
        self.bot = telebot.TeleBot(Config.SGS_TOKEN)
        self.db = DatabaseManager()
        self.tag_manager = TagManager()
        self.validator = UserValidator()
        self.suggestion_builder = SuggestionBuilder()
        self.formatter = MessageFormatter()
        
        # Статус
        self.is_running = False
        self.cleanup_thread = None
        
        # Проверка API
        if not self.db.health_check():
            logger.warning("API is not available, some features may be limited")
    
    def start(self):
        """Запуск бота"""
        logger.info("Starting Suggest Bot...")
        
        # Запуск фоновых задач
        self._start_background_tasks()
        
        # Регистрация обработчиков
        self._register_handlers()
        
        # Запуск бота
        self.is_running = True
        try:
            logger.info("Bot is running...")
            self.bot.infinity_polling()
        except Exception as e:
            logger.error(f"Bot stopped with error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Остановка бота"""
        self.is_running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        logger.info("Bot stopped")
    
    def _start_background_tasks(self):
        """Запуск фоновых задач"""
        # Очистка устаревших предложений
        def cleanup_worker():
            while self.is_running:
                time.sleep(3600)  # Каждый час
                cleaned = self.suggestion_builder.cleanup_old_suggestions()
                if cleaned > 0:
                    logger.info(f"Cleaned up {cleaned} expired suggestions")
        
        self.cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self.cleanup_thread.start()
    
    def _register_handlers(self):
        """Регистрация обработчиков команд"""
        
        # ===== КОМАНДЫ =====
        @self.bot.message_handler(commands=['start'])
        def handle_start(message: Message):
            self._handle_start(message)
        
        @self.bot.message_handler(commands=['me'])
        def handle_me(message: Message):
            self._handle_me(message)
        
        @self.bot.message_handler(commands=['help'])
        def handle_help(message: Message):
            self._handle_help(message)
        
        # ===== ПРЕДЛОЖЕНИЯ =====
        @self.bot.message_handler(content_types=Config.SUPPORTED_CONTENT_TYPES)
        def handle_suggestion(message: Message):
            self._handle_suggestion(message)
        
        # ===== НЕПОДДЕРЖИВАЕМЫЙ КОНТЕНТ =====
        @self.bot.message_handler(content_types=Config.UNSUPPORTED_CONTENT_TYPES)
        def handle_unsupported(message: Message):
            self._handle_unsupported(message)
    
    # ===== ОБРАБОТЧИКИ КОМАНД =====
    def _handle_start(self, message: Message):
        """Обработка /start"""
        # Проверка чата
        if message.chat.type != 'private' and message.chat.id != Config.SGS_CHAT_ID:
            logger.warning(f"Bot used in unauthorized chat: {message.chat.id}")
            return
        
        # Валидация пользователя
        is_valid, error_msg = self.validator.validate_user(message)
        if not is_valid:
            self.bot.reply_to(message, error_msg)
            return
        
        logger.info(f"Start command from {message.from_user.username} in chat {message.chat.id}")
        
        username = message.from_user.username.lower()
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        # Регистрация/обновление пользователя
        existing_user = self.db.get_user_by_username(username)
        
        if not existing_user:
            # Создание нового пользователя
            user_data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'rank': 'user'
            }
            
            if self.db.create_user(user_data):
                logger.info(f"New user registered: {username}")
                self.bot.reply_to(message, "✅ Вы успешно зарегистрированы в системе!")
            else:
                self.bot.reply_to(message, "❌ Ошибка при регистрации. Попробуйте позже.")
                return
        else:
            # Обновление существующего пользователя
            update_data = {
                'user_id': user_id,
                'first_name': first_name
            }
            self.db.update_user(user_id, update_data)
        
        # Приветственное сообщение
        welcome_text = (
            "🤖 **Suggest Bot - Бот для предложений**\n\n"
            "💡 **Как отправить предложение:**\n"
            "1. Напишите текст предложения или отправьте фото/видео\n"
            "2. После этого выберите подходящий тег\n"
            "3. Ваше предложение будет отправлено администраторам\n\n"
            "⚡ **Доступные команды:**\n"
            "/start - Регистрация и приветствие\n"
            "/me - Информация о вашем аккаунте\n"
            "/help - Справка по использованию\n\n"
            "📌 **Поддерживаемые форматы:**\n"
            "- Текстовые сообщения\n"
            "- Фотографии с подписью\n"
            "- Видео с описанием"
        )
        
        self.bot.reply_to(message, welcome_text, parse_mode='Markdown')
    
    def _handle_me(self, message: Message):
        """Обработка /me"""
        if message.chat.type != 'private' and message.chat.id != Config.SGS_CHAT_ID:
            return
        
        # Валидация
        is_valid, error_msg = self.validator.validate_user(message)
        if not is_valid:
            self.bot.reply_to(message, error_msg)
            return
        
        # Проверка бана
        if self.db.is_user_banned(message.from_user.id):
            self.bot.reply_to(message, "❌ Вы забанены и не можете использовать бота.")
            return
        
        logger.info(f"Me command from {message.from_user.username}")
        
        # Получение информации о пользователе
        user_data = self.db.get_user(message.from_user.id)
        
        if user_data:
            response = self.formatter.format_user_info(user_data)
            self.bot.reply_to(message, response)
        else:
            self.bot.reply_to(message, "❌ Пользователь не найден. Используйте /start для регистрации.")
    
    def _handle_help(self, message: Message):
        """Обработка /help"""
        if message.chat.type != 'private' and message.chat.id != Config.SGS_CHAT_ID:
            return
        
        # Валидация
        is_valid, error_msg = self.validator.validate_user(message)
        if not is_valid:
            self.bot.reply_to(message, error_msg)
            return
        
        # Проверка бана
        if self.db.is_user_banned(message.from_user.id):
            self.bot.reply_to(message, "❌ Вы забанены и не можете использовать бота.")
            return
        
        logger.info(f"Help command from {message.from_user.username}")
        
        help_text = (
            "🤖 **Suggest Bot - Помощь**\n\n"
            "💡 **Как отправить предложение:**\n"
            "1. Напишите текст предложения или отправьте медиа\n"
            "2. После этого выберите тег из предложенных\n"
            "3. Ваше предложение будет отправлено администраторам\n\n"
            "⚡ **Доступные команды:**\n"
            "/start - Регистрация и приветствие\n"
            "/me - Информация о вашем аккаунте\n"
            "/help - Эта справка\n\n"
            "📌 **Поддерживаемые форматы:**\n"
            "- Текстовые сообщения\n"
            "- Фотографии с подписью\n"
            "- Видео с описанием\n\n"
            "❌ **Не поддерживаются:**\n"
            "- Документы, аудио, голосовые сообщения\n"
            "- Стикеры, локации, контакты"
        )
        
        self.bot.reply_to(message, help_text, parse_mode='Markdown')
    
    # ===== ОБРАБОТЧИКИ ПРЕДЛОЖЕНИЙ =====
    def _handle_suggestion(self, message: Message):
        """Обработка предложений"""
        if message.chat.type != 'private' and message.chat.id != Config.SGS_CHAT_ID:
            return
        
        # Валидация
        is_valid, error_msg = self.validator.validate_user(message)
        if not is_valid:
            self.bot.reply_to(message, error_msg)
            return
        
        # Проверка бана
        if self.db.is_user_banned(message.from_user.id):
            self.bot.reply_to(message, "❌ Вы забанены и не можете отправлять предложения.")
            return
        
        username = message.from_user.username
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Проверяем, не является ли это выбором тега
        tags = self.tag_manager.load_tags()
        if message.text in tags or message.text == "📤 Отправить без тега":
            self._handle_tag_selection(message)
        else:
            # Это новое предложение
            logger.info(f"Suggestion content from @{username}")
            
            # Получаем данные пользователя
            user_data = self.db.get_user(user_id)
            if not user_data:
                self.bot.reply_to(message, "❌ Вы не зарегистрированы. Используйте /start")
                return
            
            # Создаем предложение
            suggestion = self.suggestion_builder.create_suggestion(chat_id, message, user_data)
            
            # Предлагаем выбрать тег
            keyboard = self.tag_manager.create_tags_keyboard()
            self.bot.send_message(
                chat_id,
                "✅ Содержание получено! Теперь выберите тег для вашего предложения:",
                reply_markup=keyboard
            )
    
    def _handle_tag_selection(self, message: Message):
        """Обработка выбора тега"""
        tags = self.tag_manager.load_tags()
        chat_id = message.chat.id
        username = message.from_user.username
        
        # Проверяем активное предложение
        suggestion = self.suggestion_builder.get_suggestion(chat_id)
        if not suggestion:
            self.bot.send_message(chat_id, "❌ Сначала отправьте предложение (текст, фото или видео).")
            return
        
        # Проверяем владельца
        if suggestion['username'] != username:
            self.bot.send_message(chat_id, "❌ Это предложение принадлежит другому пользователю.")
            return
        
        # Определяем выбранный тег
        if message.text == "📤 Отправить без тега":
            selected_tag = None
            tag_info_text = "без тега"
        else:
            tag_name = message.text
            hashtag = tags.get(tag_name, "")
            selected_tag = {
                'tag_name': tag_name,
                'hashtag': hashtag
            }
            tag_info_text = f"с тегом {tag_name}"
        
        try:
            # Формируем подпись
            caption = self.formatter.format_suggestion_caption(suggestion, selected_tag)
            
            # Отправляем в целевой чат
            if suggestion['content_type'] == 'text':
                full_text = f"{caption}\n\n{suggestion['text']}"
                self.bot.send_message(Config.SGS_CHAT_ID, full_text, parse_mode='HTML')
                
            elif suggestion['content_type'] == 'photo':
                if suggestion.get('text'):
                    full_caption = f"{caption}\n\n{suggestion['text']}"
                else:
                    full_caption = caption
                
                self.bot.send_photo(
                    Config.SGS_CHAT_ID, 
                    suggestion['photo'], 
                    caption=full_caption,
                    parse_mode='HTML'
                )
                
            elif suggestion['content_type'] == 'video':
                if suggestion.get('text'):
                    full_caption = f"{caption}\n\n{suggestion['text']}"
                else:
                    full_caption = caption
                
                self.bot.send_video(
                    Config.SGS_CHAT_ID,
                    suggestion['video'],
                    caption=full_caption,
                    parse_mode='HTML'
                )
            
            # Очищаем временные данные
            self.suggestion_builder.remove_suggestion(chat_id)
            
            # Убираем клавиатуру
            self.bot.send_message(
                chat_id,
                f"✅ Ваше предложение отправлено {tag_info_text}!",
                reply_markup=telebot.types.ReplyKeyboardRemove(selective=False)
            )
            
            logger.info(f"Suggestion from @{username} forwarded to chat {Config.SGS_CHAT_ID} {tag_info_text}")
            
        except Exception as e:
            logger.error(f"Error forwarding suggestion from @{username}: {e}")
            self.bot.send_message(chat_id, "❌ Ошибка при отправке предложения. Попробуйте позже.")
    
    def _handle_unsupported(self, message: Message):
        """Обработка неподдерживаемого контента"""
        if message.chat.type != 'private' and message.chat.id != Config.SGS_CHAT_ID:
            return
        
        self.bot.reply_to(
            message,
            "❌ Поддерживаются только текст, фото и видео. Другие типы сообщений не принимаются."
        )
        logger.warning(f"Unsupported content from {message.from_user.username}: {message.content_type}")


def main():
    """Точка входа"""
    try:
        bot = SuggestBot()
        bot.start()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()