import os
import json
import logging
import time
from datetime import datetime
import telebot
from telebot.types import Message
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
MAX_WARN = os.getenv('MAX_WARN')
SUPER_OPERATOR = os.getenv('SUPER_OPERATOR', 'ghoulyonok')

if not SGS_TOKEN:
    logger.error("SGS_TOKEN not found in environment variables")
    exit(1)

# Инициализация бота
bot = telebot.TeleBot(SGS_TOKEN)

# Пути к файлам данных
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
BANNED_FILE = os.path.join(DATA_DIR, 'banned.json')
ADMINS_FILE = os.path.join(DATA_DIR, 'admins.json')
BOTS_DATA_FILE = os.path.join(DATA_DIR, 'bots_data.json')
AUTH_CODES_FILE = os.path.join(DATA_DIR, 'auth_codes.json')
WELCOME_MESSAGE_FILE = os.path.join(DATA_DIR, 'welcome_message.txt')

# Словарь для рангов
RANK_TEXTS = {
    'operator': '⚡ Оператор',
    'gadmin': '🔧 Глобальный администратор',
    'ladmin': '🪛 Локальный администратор',
    'user': '👤 Пользователь'
}


# Вспомогательные функции
def load_json(file_path):
    """Загрузка JSON файла"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return {}


def save_json(file_path, data):
    """Сохранение данных в JSON файл"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving {file_path}: {e}")
        return False


def is_user_allowed(message: Message):
    """Проверка, может ли пользователь использовать бота"""
    # Проверка на наличие username
    if not message.from_user.username:
        bot.send_message(message.chat.id, "❌ Для использования бота необходимо иметь username.")
        return False

    username = message.from_user.username.lower()

    # Загрузка данных
    users = load_json(USERS_FILE)
    banned = load_json(BANNED_FILE)

    # Проверка на наличие в системе
    if username not in users:
        bot.send_message(message.chat.id, "❌ Вы не зарегистрированы в системе. Используйте /start для регистрации.")
        return False

    # Проверка на бан
    if username in banned:
        ban_data = banned[username]
        ban_time = ban_data.get('ban_time', 0)
        banned_at = ban_data.get('banned_at', 0)

        if ban_time == 0:  # Перманентный бан
            bot.send_message(message.chat.id, "❌ Вы забанены навсегда.")
            return False
        elif time.time() < banned_at + (ban_time * 3600):  # Временный бан еще активен
            remaining = int((banned_at + (ban_time * 3600) - time.time()) / 60)
            bot.send_message(message.chat.id, f"❌ Вы забанены. Осталось: {remaining} минут.")
            return False
        else:  # Бан истек
            del banned[username]
            save_json(BANNED_FILE, banned)

    return True


def get_user_rank(username):
    """Получение ранга пользователя"""
    users = load_json(USERS_FILE)
    admins = load_json(ADMINS_FILE)

    if username in users:
        user_data = users[username]
        rank = user_data.get('rank', 'user')

        # Дополнительная проверка для глобальных админов и операторов
        if rank == 'gadmin' and username not in admins.get('global_admins', []):
            rank = 'user'
        elif rank == 'operator' and username not in admins.get('operators', []):
            rank = 'user'

        return rank
    return 'user'


def is_admin(username):
    """Проверка, является ли пользователь администратором"""
    rank = get_user_rank(username)
    return rank in ['gadmin', 'operator']


def get_welcome_message():
    """Получение приветственного сообщения"""
    try:
        if os.path.exists(WELCOME_MESSAGE_FILE):
            with open(WELCOME_MESSAGE_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip()
    except Exception as e:
        logger.error(f"Error reading welcome message: {e}")
    return "Добро пожаловать! Используйте /help для получения справки."


def save_welcome_message(text):
    """Сохранение приветственного сообщения"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(WELCOME_MESSAGE_FILE, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception as e:
        logger.error(f"Error saving welcome message: {e}")
        return False


# Обработчики команд
@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    """Обработка команды /start"""

    # Проверка типа чата
    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        logger.warning(f"Bot used in unauthorized chat: {message.chat.id}")
        return

    if not message.from_user.username:
        bot.send_message(message.chat.id, "❌ Для использования бота необходимо иметь username.")
        return

    logger.info(f"Start command from {message.from_user.username} in chat {message.chat.id}")

    username = message.from_user.username.lower()
    users = load_json(USERS_FILE)

    # Регистрация нового пользователя
    if username not in users:
        users[username] = {
            "id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "rank": "user",
            "banned": False,
            "warns": 0
        }
        if save_json(USERS_FILE, users):
            logger.info(f"New user registered: {username}")
            bot.send_message(message.chat.id, "✅ Вы успешно зарегистрированы в системе!")
        else:
            logger.error(f"Failed to register user: {username}")
            bot.send_message(message.chat.id, "❌ Ошибка регистрации. Попробуйте позже.")
            return

    # Отправка приветственного сообщения
    welcome_msg = get_welcome_message()
    bot.send_message(message.chat.id, welcome_msg)


@bot.message_handler(commands=['chatid'])
def handle_chatid(message: Message):
    """Обработка команды /chatid"""

    if not message.from_user.username:
        bot.send_message(message.chat.id, "❌ Для использования бота необходимо иметь username.")
        return

    logger.info(f"Chatid command from {message.from_user.username} in chat {message.chat.id}")

    username = message.from_user.username.lower()
    users = load_json(USERS_FILE)

    if is_admin(message.from_user.username):
        bot.send_message(message.chat.id, f"Chat ID: <code>{message.chat.id}</code>", parse_mode='HTML')


@bot.message_handler(commands=['me'])
def handle_me(message: Message):
    """Обработка команды /me"""

    # Проверка типа чата
    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        return

    if not is_user_allowed(message):
        return

    logger.info(f"Me command from {message.from_user.username}")


    username = message.from_user.username.lower()
    users = load_json(USERS_FILE)
    banned = load_json(BANNED_FILE)

    if username in users:
        user_data = users[username]
        rank = get_user_rank(username)
        rank_text = RANK_TEXTS.get(rank, '👤 Пользователь')

        # Проверка бана
        banned_status = "❌ Забанен" if username in banned else "✅ Активен"

        if rank in ['gadmin', 'operator']:
            response = (
                f"👤 Информация о пользователе\n\n"
                f"📧 Username: @{username}\n"
                f"👨‍💼 Ранг: {rank_text}\n"
                f"🆔 ID: {user_data['id']}\n"
                f"📛 Имя: {user_data['first_name']}"
            )
        else:
            response = (
                f"👤 Информация о пользователе\n\n"
                f"📧 Username: @{username}\n"
                f"👨‍💼 Ранг: {rank_text}\n"
                f"🆔 ID: {user_data['id']}\n"
                f"📛 Имя: {user_data['first_name']}\n"
                f"📊 Ограничения: {banned_status}\n"
                f"💢 Предупреждения: {user_data['warns']}/{MAX_WARN}"
            )

        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "❌ Пользователь не найден в системе.")


@bot.message_handler(commands=['help'])
def handle_help(message: Message):
    """Обработка команды /help"""

    # Проверка типа чата
    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        return

    if not is_user_allowed(message):
        return

    logger.info(f"Help command from {message.from_user.username}")

    help_text = (
        "🤖 **Suggest Bot - Помощь**\n\n"
        "📝 **Как отправить предложение:**\n"
        "Просто отправьте боту сообщение с текстом, фото или видео.\n\n"
        "⚡ **Доступные команды:**\n"
        "/start - Регистрация и приветствие\n"
        "/me - Информация о вашем аккаунте\n"
        "/help - Эта справка\n\n"
        "📌 **Важно:**\n"
        "- Предложения должны быть содержательными\n"
        "- Запрещены спам и оскорбления\n"
        "- Только текст, фото и видео"
    )

    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


@bot.message_handler(commands=['setmg'])
def handle_setmg(message: Message):
    """Обработка команды /setmg для администраторов"""

    # Проверка типа чата
    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        return

    if not is_user_allowed(message):
        return

    username = message.from_user.username.lower()

    logger.info(f"Setmg command from {message.from_user.username}")

    # Проверка прав администратора
    if not is_admin(username):
        bot.send_message(message.chat.id, "❌ Недостаточно прав. Только для администраторов.")
        return

    # Извлечение текста из команды
    text = message.text.split(' ', 1)
    if len(text) < 2:
        bot.send_message(message.chat.id, "❌ Использование: /setmg [текст]")
        return

    new_message = text[1].strip()
    if save_welcome_message(new_message):
        bot.send_message(message.chat.id, "✅ Приветственное сообщение обновлено!")
        logger.info(f"Welcome message updated by {username}")
    else:
        bot.send_message(message.chat.id, "❌ Ошибка при сохранении сообщения.")
        logger.error(f"Failed to update welcome message by {username}")


@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_suggestion(message: Message):
    """Обработка предложений от пользователей"""

    # Проверка типа чата
    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        return

    if not is_user_allowed(message):
        return

    username = message.from_user.username
    user_id = message.from_user.id

    logger.info(f"Suggestion from {message.from_user.username}")
    try:
        # Отправка в целевой чат
        caption = f"💡 Предложение от @{username} (ID: {user_id})"
        full_text = f"{caption}\n\n{message.text}"

        if message.content_type == 'text':
            full_text = f"{caption}\n\n{message.text}"
            bot.send_message(SGS_CHAT_ID, full_text)

        elif message.content_type == 'photo':
            # Берем фото максимального качества
            photo = message.photo[-1].file_id
            full_text = f"{caption}\n\n{message.caption}"
            bot.send_photo(SGS_CHAT_ID, photo, caption=full_text)

        elif message.content_type == 'video':
            video = message.video.file_id
            full_text = f"{caption}\n\n{message.caption}"
            bot.send_video(SGS_CHAT_ID, video, caption=full_text)

        # Подтверждение пользователю
        bot.send_message(message.chat.id, "✅ Ваше предложение отправлено!")
        logger.info(f"Suggestion from @{username} forwarded to chat {SGS_CHAT_ID}")

    except Exception as e:
        logger.error(f"Error forwarding suggestion from @{username}: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при отправке предложения. Попробуйте позже.")


@bot.message_handler(content_types=['document', 'audio', 'voice', 'sticker', 'location', 'contact'])
def handle_unsupported_content(message: Message):
    """Обработка неподдерживаемых типов контента"""

    # Проверка типа чата
    if message.chat.type != 'private' and message.chat.id != SGS_CHAT_ID:
        return

    if not is_user_allowed(message):
        return

    bot.send_message(
        message.chat.id,
        "❌ Поддерживаются только текст, фото и видео. Другие типы сообщений не принимаются."
    )

    logger.warning(f"Unsupported content from {message.from_user.username}: {message.content_type}")

def main():
    """Основная функция запуска бота"""
    logger.info("Starting Suggest Bot...")
    logger.info(f"Target chat ID: {SGS_CHAT_ID}")
    logger.info(f"Data directory: {DATA_DIR}")

    # Проверка существования директорий
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.getenv('LOGS_DIR', 'logs'), exist_ok=True)

    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
    finally:
        logger.info("Suggest Bot stopped")


if __name__ == "__main__":
    main()