import os
import json
import logging
import time
import sqlite3
from datetime import datetime
import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.getenv('LOGS_DIR', 'logs'), 'sgs-bot.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('sgs-bot')

# Конфигурация бота
SGS_TOKEN = os.getenv('SGS_TOKEN')
SGS_CHAT_ID = os.getenv('SGS_CHAT_ID')

DATA_DIR = os.getenv('DATA_DIR', 'data')
DB_PATH = os.path.join(DATA_DIR, 'system.db')
TAGS_FILE = os.path.join(DATA_DIR, 'tags.json')

MAX_WARN = os.getenv('MAX_WARN')

if not SGS_TOKEN:
    logger.error("SGS_TOKEN not found in environment variables")
    exit(1)

# Инициализация бота
bot = telebot.TeleBot(SGS_TOKEN)

# Словарь для рангов
RANK_TEXTS = {
    'operator': '⚡ Оператор',
    'gadmin': '🔧 Глобальный администратор',
    'ladmin': '🪛 Локальный администратор',
    'user': '👤 Пользователь'
}

# Вспомогательные функции
def get_db_connection():
    """Создание соединения с базой данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def is_user_allowed(message: Message):
    """Проверка, может ли пользователь использовать бота"""
    if not message.from_user.username:
        bot.reply_to(message, "❌ Для использования бота необходимо иметь username.")
        return False

    username = message.from_user.username.lower()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверка на наличие в системе
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        bot.reply_to(message, "❌ Вы не зарегистрированы в системе. Используйте /start для регистрации.")
        conn.close()
        return False

    # Проверка на бан
    cursor.execute("SELECT * FROM bans WHERE username = ?", (username,))
    ban = cursor.fetchone()

    if ban:
        banned_at = ban['banned_at']
        ban_time = ban['ban_time']

        if ban_time == 0:  # Перманентный бан
            bot.reply_to(message, "❌ Вы забанены навсегда.")
            conn.close()
            return False
        elif time.time() < banned_at + (ban_time * 3600):  # Временный бан еще активен
            remaining = int((banned_at + (ban_time * 3600) - time.time()) / 60)
            bot.reply_to(message, f"❌ Вы забанены. Осталось: {remaining} минут.")
            conn.close()
            return False
        else:  # Бан истек
            cursor.execute("DELETE FROM bans WHERE username = ?", (username,))
            conn.commit()

    conn.close()
    return True

def get_user_rank(username):
    """Получение ранга пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT rank FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        rank = user['rank']

        # Дополнительная проверка для глобальных админов и операторов
        if rank == 'gadmin':
            cursor.execute("SELECT * FROM global_admins WHERE username = ?", (username,))
            if not cursor.fetchone():
                rank = 'user'
        elif rank == 'operator':
            cursor.execute("SELECT * FROM operators WHERE username = ?", (username,))
            if not cursor.fetchone():
                rank = 'user'

    conn.close()
    return rank if user else 'user'

def is_admin(username):
    """Проверка, является ли пользователь администратором"""
    rank = get_user_rank(username)
    return rank in ['gadmin', 'operator']

def load_tags():
    """Загрузка тегов из JSON файла"""
    try:
        if os.path.exists(TAGS_FILE):
            with open(TAGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading tags: {e}")
        return {}

def save_tags(tags_data):
    """Сохранение тегов в JSON файл"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(TAGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tags_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving tags: {e}")
        return False

def create_tags_keyboard():
    """Создание клавиатуры с тегами"""
    tags = load_tags()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    if tags:
        # Добавляем кнопки для каждого тега
        tag_buttons = [KeyboardButton(tag_name) for tag_name in tags.keys()]

        # Разбиваем на ряды по 2 кнопки
        for i in range(0, len(tag_buttons), 2):
            if i + 1 < len(tag_buttons):
                keyboard.add(tag_buttons[i], tag_buttons[i + 1])
            else:
                keyboard.add(tag_buttons[i])

    # Кнопка для отправки без тега
    keyboard.add(KeyboardButton("📤 Отправить без тега"))

    return keyboard

def handle_suggestion(message: Message):
    """Обработка предложений от пользователей"""
    username = message.from_user.username
    user_id = message.from_user.id
    chat_id = message.chat.id

    logger.info(f"Suggestion content from @{username}")

    # Сохраняем предложение во временное хранилище
    user_suggestions[chat_id] = {
        'username': username,
        'user_id': user_id,
        'content_type': message.content_type,
        'text': message.text if message.content_type == 'text' else None,
        'photo': message.photo[-1].file_id if message.content_type == 'photo' else None,
        'video': message.video.file_id if message.content_type == 'video' else None,
        'caption': message.caption if message.content_type in ['photo', 'video'] else None,
        'timestamp': time.time()
    }

    # Предлагаем выбрать тег через обычную клавиатуру
    keyboard = create_tags_keyboard()
    bot.send_message(
        chat_id,
        "✅ Содержание получено! Теперь выберите тег для вашего предложения:",
        reply_markup=keyboard
    )

def handle_tag_selection(message: Message):
    """Обработка выбора тега через обычную клавиатуру"""

    tags = load_tags()
    chat_id = message.chat.id
    username = message.from_user.username

    # Проверяем, есть ли активное предложение для этого чата
    if chat_id not in user_suggestions:
        bot.send_message(chat_id, "❌ Сначала отправьте предложение (текст, фото или видео).")
        return

    suggestion = user_suggestions[chat_id]

    # Проверяем, что предложение принадлежит текущему пользователю
    if suggestion['username'] != username:
        bot.send_message(chat_id, "❌ Это предложение принадлежит другому пользователю.")
        return

    # Определяем выбранный тег
    if message.text == "📤 Отправить без тега":
        selected_tag = None
        tag_info = "без тега"
    else:
        tag_name = message.text
        hashtag = tags.get(tag_name, "")
        selected_tag = {
            'tag_name': tag_name,
            'hashtag': hashtag
        }
        tag_info = f"с тегом {tag_name}"

    try:
        # Формируем заголовок
        base_caption = f"💡 Suggestion from @{suggestion['username']} (ID: {suggestion['user_id']})"

        if selected_tag and selected_tag['hashtag']:
            base_caption += f"\n🏷️ Tags: {selected_tag['hashtag']}"

        # Отправка в целевой чат
        if suggestion['content_type'] == 'text':
            full_text = f"{base_caption}\n\n{suggestion['text']}"
            bot.send_message(SGS_CHAT_ID, full_text)

        elif suggestion['content_type'] == 'photo':
            caption_text = suggestion['caption'] or ""
            full_caption = f"{base_caption}\n\n{caption_text}"
            bot.send_photo(SGS_CHAT_ID, suggestion['photo'], caption=full_caption)

        elif suggestion['content_type'] == 'video':
            caption_text = suggestion['caption'] or ""
            full_caption = f"{base_caption}\n\n{caption_text}"
            bot.send_video(SGS_CHAT_ID, suggestion['video'], caption=full_caption)

        # Удаляем временные данные
        del user_suggestions[chat_id]

        # Убираем клавиатуру
        bot.send_message(
            chat_id,
            f"✅ Ваше предложение отправлено {tag_info}!",
            reply_markup=ReplyKeyboardRemove(selective=False)
        )

        logger.info(f"Suggestion from @{username} forwarded to chat {SGS_CHAT_ID} {tag_info}")

    except Exception as e:
        logger.error(f"Error forwarding suggestion from @{username}: {e}")
        bot.send_message(chat_id, "❌ Ошибка при отправке предложения. Попробуйте позже.")

# Переменная для хранения временных данных о предложениях
user_suggestions = {}

# Обработчики команд
@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    """Обработка команды /start"""
    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        logger.warning(f"Bot used in unauthorized chat: {message.chat.id}")
        return

    if not message.from_user.username:
        bot.reply_to(message, "❌ Для использования бота необходимо иметь username.")
        return

    logger.info(f"Start command from {message.from_user.username} in chat {message.chat.id}")

    username = message.from_user.username.lower()
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    conn = get_db_connection()
    cursor = conn.cursor()

    # Регистрация нового пользователя
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (username, user_id, first_name, rank) VALUES (?, ?, ?, ?)",
            (username, user_id, first_name, 'user')
        )
        conn.commit()
        logger.info(f"New user registered: {username}")
        bot.reply_to(message, "✅ Вы успешно зарегистрированы в системе!")
    else:
        # Обновление информации о пользователе
        cursor.execute(
            "UPDATE users SET user_id = ?, first_name = ?, updated_at = CURRENT_TIMESTAMP WHERE username = ?",
            (user_id, first_name, username)
        )
        conn.commit()

    conn.close()

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

    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['me'])
def handle_me(message: Message):
    """Обработка команды /me"""
    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        return

    if not is_user_allowed(message):
        return

    logger.info(f"Me command from {message.from_user.username}")

    username = message.from_user.username.lower()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM bans WHERE username = ?", (username,))
    ban = cursor.fetchone()

    if user:
        rank = get_user_rank(username)
        rank_text = RANK_TEXTS.get(rank, '👤 Пользователь')

        # Проверка бана
        banned_status = "❌ Забанен" if ban else "✅ Отсутствуют"

        # Исправление: правильное получение значений из sqlite3.Row
        response = (
            f"👤 Информация о пользователе\n\n"
            f"📧 Username: @{username}\n"
            f"👨‍💼 Ранг: {rank_text}\n"
            f"🆔 ID: {user['user_id']}\n"  # Исправлено: user['id'] вместо user.get('id')
            f"📛 Имя: {user['first_name']}"  # Исправлено: user['first_name'] вместо user.get('first_name')
        )

        if rank not in ['gadmin', 'operator']:
            # Исправлено: правильное получение значения warns
            warns = user['warns'] if 'warns' in user.keys() else 0
            response += (
                f"\n📊 Ограничения: {banned_status}\n"
                f"💢 Предупреждения: {warns}/{MAX_WARN}"
            )

        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "❌ Пользователь не найден в системе.")

    conn.close()

@bot.message_handler(commands=['help'])
def handle_help(message: Message):
    """Обработка команды /help"""
    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        return

    if not is_user_allowed(message):
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

    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(content_types=['document', 'audio', 'voice', 'sticker', 'location', 'contact'])
def handle_unsupported_content(message: Message):
    """Обработка неподдерживаемых типов контента"""
    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        return

    if not is_user_allowed(message):
        return

    bot.send_message(
        message.chat.id,
        "❌ Поддерживаются только текст, фото и видео. Другие типы сообщений не принимаются."
    )
    logger.warning(f"Unsupported content from {message.from_user.username}: {message.content_type}")

@bot.message_handler(content_types=['text', 'photo', 'video'], func=lambda message: True)
def handle_text(message: Message):

    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        return

    if not is_user_allowed(message):
        return

    # Проверяем, не является ли это сообщение выбором тега
    tags = load_tags()
    if message.text in tags or message.text == "📤 Отправить без тега":
        handle_tag_selection(message)
    else:
        handle_suggestion(message)

def cleanup_old_suggestions():
    """Очистка устаревших предложений (старше 1 часа)"""
    current_time = time.time()
    expired_chats = []

    for chat_id, suggestion in user_suggestions.items():
        if current_time - suggestion['timestamp'] > 3600:  # 1 час
            expired_chats.append(chat_id)

    for chat_id in expired_chats:
        del user_suggestions[chat_id]

    if expired_chats:
        logger.info(f"Cleaned up {len(expired_chats)} expired suggestions")

def main():
    """Основная функция запуска бота"""
    logger.info("Starting Suggest Bot...")
    logger.info(f"Target chat ID: {SGS_CHAT_ID}")
    logger.info(f"Data directory: {DATA_DIR}")

    # Проверка существования директорий
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.getenv('LOGS_DIR', 'logs'), exist_ok=True)

    # Проверка существования файла тегов
    if not os.path.exists(TAGS_FILE):
        logger.info("Tags file not found, creating default tags...")
        default_tags = {
            "🐛 Баг": "#баг",
            "💡 Идея": "#идея",
            "🚀 Улучшение": "#улучшение",
            "📝 Документация": "#документация",
            "🎨 Дизайн": "#дизайн"
        }
        save_tags(default_tags)
        logger.info("Default tags created")

    # Запускаем периодическую очистку устаревших предложений
    import threading
    def cleanup_worker():
        while True:
            time.sleep(3600)  # Проверка каждый час
            cleanup_old_suggestions()

    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()

    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
    finally:
        logger.info("Suggest Bot stopped")

if __name__ == "__main__":
    main()