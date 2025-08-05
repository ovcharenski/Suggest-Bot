import time
import telebot
from telebot.types import Message
from config import BOT_TOKEN, ADMIN_CHAT_ID
from database import readcsv, changecsv, deluser, adduser
from logger import logger

bot = telebot.TeleBot(BOT_TOKEN)


def is_admin(message: Message) -> bool:
    """Проверяет, является ли пользователь администратором"""
    try:
        return message.from_user.username in readcsv("admin")
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False


def safe_send_message(chat_id, text, **kwargs):
    """Безопасная отправка сообщений с обработкой ошибок"""
    try:
        return bot.send_message(chat_id, text, **kwargs)
    except telebot.apihelper.ApiException as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
        return None


def safe_reply_to(message, text, **kwargs):
    """Безопасный ответ на сообщение"""
    try:
        return bot.reply_to(message, text, **kwargs)
    except Exception as e:
        logger.error(f"Failed to reply to message {message.message_id}: {e}")
        return safe_send_message(message.chat.id, text, **kwargs)


@bot.message_handler(commands=['start'])
def start(message: Message):
    """Обработчик команды /start"""
    try:
        if message.chat.id not in ADMIN_CHAT_ID:
            # Регистрация пользователя
            if message.from_user.username not in readcsv("reg"):
                if not changecsv("reg", message):
                    logger.warning(f"Failed to register user @{message.from_user.username}")

            # Приветственное сообщение
            safe_send_message(message.chat.id, f"<em><b>Hello @{message.from_user.username}!</b></em>", parse_mode='html')
            safe_send_message(message.chat.id,
                              "<em><b>Suggest your song!)\n\nArtist - Title</b></em>",
                              parse_mode='html')
    except Exception as e:
        logger.error(f"Error in start handler: {e}")


@bot.message_handler(commands=['id'])
def getid(message: Message):
    """Получение ID пользователя"""
    try:
        if not is_admin(message):
            return

        if message.reply_to_message:
            user = message.reply_to_message.from_user
            response = f"ID: <code>{user.id}</code>"
        elif "@" in message.text:
            username = message.text.split()[1][1:]
            reg_data = readcsv("reg")
            if username in reg_data:
                response = f"ID: <code>{reg_data[username][1]}</code>"
            else:
                response = "Error 101: UserNotFound"
        else:
            response = f"ID: <code>{message.from_user.id}</code>"

        safe_reply_to(message, response, parse_mode='html')
    except Exception as e:
        logger.error(f"Error in id handler: {e}")
        safe_reply_to(message, "Error processing request")


@bot.message_handler(commands=['info'])
def getinfo(message: Message):
    """Получение информации о пользователе"""
    try:
        if not is_admin(message):
            return

        if message.reply_to_message:
            user = message.reply_to_message.from_user
            response = (f"@{user.username}\n"
                        f"{user.first_name}\n"
                        f"ID: <code>{user.id}</code>")
        elif "@" in message.text:
            username = message.text.split()[1][1:]
            reg_data = readcsv("reg")
            if username in reg_data:
                response = (f"@{username}\n"
                            f"{reg_data[username][0]}\n"
                            f"ID: <code>{reg_data[username][1]}</code>")
            else:
                response = "Error 101: UserNotFound"
        else:
            response = (f"@{message.from_user.username}\n"
                        f"{message.from_user.first_name}\n"
                        f"ID: <code>{message.from_user.id}</code>")

        safe_reply_to(message, response, parse_mode='html')
    except Exception as e:
        logger.error(f"Error in info handler: {e}")
        safe_reply_to(message, "Error processing request")


@bot.message_handler(commands=['chat'])
def getchat(message: Message):
    """Получение ID чата"""
    try:
        if not is_admin(message):
            return
        safe_reply_to(message, f"Chat ID: <code>{message.chat.id}</code>", parse_mode='html')
    except Exception as e:
        logger.error(f"Error in chat id handler: {e}")
        safe_reply_to(message, "Error processing request")


@bot.message_handler(commands=['ban'])
def ban(message: Message):
    """Блокировка пользователя"""
    try:
        if message.chat.id not in ADMIN_CHAT_ID or not message.text or "@" not in message.text:
            return

        username = message.text.split()[1][1:]
        if adduser("banned", username):
            safe_reply_to(message, "User banned successfully!")
            logger.info(f"User @{username} banned by @{message.from_user.username}")
        else:
            safe_reply_to(message, "Failed to ban user")
    except IndexError:
        safe_reply_to(message, "Usage: /ban @username")
    except Exception as e:
        logger.error(f"Error in ban handler: {e}")
        safe_reply_to(message, "Error banning user")


@bot.message_handler(commands=['unban'])
def unban(message: Message):
    """Разблокировка пользователя"""
    try:
        if message.chat.id not in ADMIN_CHAT_ID or not message.text or "@" not in message.text:
            return

        username = message.text.split()[1][1:]
        if deluser("banned", username):
            safe_reply_to(message, "User unbanned successfully!")
            logger.info(f"User @{username} unbanned by @{message.from_user.username}")
        else:
            safe_reply_to(message, "User not found in ban list")
    except IndexError:
        safe_reply_to(message, "Usage: /unban @username")
    except Exception as e:
        logger.error(f"Error in unban handler: {e}")
        safe_reply_to(message, "Error unbanning user")


@bot.message_handler(commands=['op'])
def op(message: Message):
    """Повышение пользователя"""
    try:
        if message.chat.id not in ADMIN_CHAT_ID:
            return

        if "@" in message.text or not (message.text or message.reply_to_message):
            safe_reply_to(message, f"Error 101: UserNotFound")

        user = message.reply_to_message.from_user
        if adduser("admin", user.username, user.first_name, user.id):
            safe_reply_to(message, "User promoted successfully!")
            logger.info(f"User @{user.username} promoted by @{message.from_user.username}")
        else:
            safe_reply_to(message, "Failed to promote user")
    except IndexError:
        safe_reply_to(message, "Usage: /op [with reply]")
    except Exception as e:
        logger.error(f"Error in promote handler: {e}")
        safe_reply_to(message, "Error promoting user")


@bot.message_handler(commands=['unop'])
def unop(message: Message):
    """Понижение пользователя"""
    try:
        if message.chat.id not in ADMIN_CHAT_ID:
            return

        if not (message.text or "@" in message.text or message.reply_to_message):
            safe_reply_to(message, f"Error 101: UserNotFound")

        if message.reply_to_message:
            username = message.reply_to_message.from_user.username
        else:
            username = message.text.split()[1][1:]
        userid = readcsv("admin")[username][1]

        if deluser("admin", username):
            safe_reply_to(message, "User demoted successfully!")
            bot.kick_chat_member(chat_id=message.chat.id, user_id=userid)
            logger.info(f"User @{username} demoted by @{message.from_user.username}")
        else:
            safe_reply_to(message, "User not found in ban list")
    except IndexError:
        safe_reply_to(message, "Usage: /unop @username or [with reply]")
    except Exception as e:
        logger.error(f"Error in demote handler: {e}")
        safe_reply_to(message, "Error demoting user")


@bot.message_handler(commands=['banlist'])
def banlist(message: Message):
    """Показать список заблокированных пользователей"""
    try:
        if message.chat.id not in ADMIN_CHAT_ID:
            return

        banned_users = readcsv("banned")
        if not banned_users:
            safe_reply_to(message, "Ban list is empty")
            return

        message_text = "🤬 <b>BAN LIST</b> 🤬\n\n"
        for idx, (username, user_data) in enumerate(banned_users.items(), 1):
            message_text += (f"{idx}. @{username}\n"
                             f"    {user_data[0]}\n"
                             f"    ID: <code>{user_data[1]}</code>\n\n")

        safe_reply_to(message, message_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in banlist handler: {e}")
        safe_reply_to(message, "Error retrieving ban list")


@bot.message_handler(commands=['adminlist'])
def adminlist(message: Message):
    """Показать список админов"""
    try:
        if message.chat.id not in ADMIN_CHAT_ID:
            return

        admin_users = readcsv("admin")
        if not admin_users:
            safe_reply_to(message, "Admin list is empty")
            return

        message_text = "✨ <b>ADMIN LIST</b> ✨\n\n"
        for idx, (username, user_data) in enumerate(admin_users.items(), 1):
            message_text += (f"{idx}. @{username}\n"
                             f"    {user_data[0]}\n"
                             f"    ID: <code>{user_data[1]}</code>\n\n")

        safe_reply_to(message, message_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in adminlist handler: {e}")
        safe_reply_to(message, "Error retrieving admin list")


@bot.message_handler(commands=['alarm'])
def alarm(message: Message):
    """Созвать всех админов"""
    try:
        if message.chat.id not in ADMIN_CHAT_ID:
            return

        if not message.reply_to_message:
            safe_reply_to(message, f"Error 102: MessageNotFound")
            return

        admin_users = readcsv("admin")
        if not admin_users:
            safe_reply_to(message, "Admin list is empty")
            return

        message_text = "🚨 ALARM 🚨\n\n"
        for username in admin_users.keys():
            message_text += f"@{username} "

        safe_reply_to(message.reply_to_message, message_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in alarm handler: {e}")
        safe_reply_to(message, "Error alarm")


@bot.message_handler(commands=['announce'])
def announce(message: Message):
    """Отправка объявления всем пользователям"""
    try:
        if not is_admin(message):
            return

        text = message.text[9:].strip()
        if not text:
            safe_reply_to(message, "Error 103: TextNotFound")
            return

        reg_users = readcsv("reg")
        if not reg_users:
            safe_reply_to(message, "Error 101: UserNotFound")
            return

        total = 0
        failed = 0
        for username, user_data in reg_users.items():
            try:
                if safe_send_message(user_data[1], text):
                    total += 1
                else:
                    failed += 1
                time.sleep(0.1)  # Задержка чтобы не превысить лимиты API
            except Exception as e:
                logger.error(f"Error sending to @{username}: {e}")
                failed += 1

        report = (f"Announcement delivered to {total} users\n"
                  f"Failed to deliver to {failed} users")
        safe_reply_to(message, report)
        logger.info(f"Announcement sent by @{message.from_user.username}: {total} successful, {failed} failed")
    except Exception as e:
        logger.error(f"Error in announce handler: {e}")
        safe_reply_to(message, "Error sending announcements")


@bot.message_handler(func=lambda message: True)
def handle_suggestion(message: Message):
    """Обработка предложений песен"""
    try:
        if message.chat.id == ADMIN_CHAT_ID or is_admin(message):
            return

        if message.from_user.username in readcsv("banned"):
            safe_send_message(message.chat.id,
                              "<em><b>You are banned for rule violation!</b></em>",
                              parse_mode='html')
            logger.info(f"Banned user @{message.from_user.username} tried to send message")
        else:
            safe_send_message(message.chat.id,
                              "<em><b>Your suggestion was received!</b></em>",
                              parse_mode='html')

            # Отправка предложения в админ-чат
            admin_message = (f"<em><b>New suggestion from @{message.from_user.username}:\n\n"
                             f"{message.text}</b></em>")
            if not safe_send_message(ADMIN_CHAT_ID, admin_message, parse_mode='html'):
                logger.error("Failed to forward suggestion to admin chat")

            logger.info(f"New suggestion from @{message.from_user.username}")
    except Exception as e:
        logger.error(f"Error handling suggestion: {e}")


def run_bot():
    """Запуск бота с обработкой ошибок"""
    logger.info("Starting Suggest Bot")
    while True:
        try:
            bot.infinity_polling()
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f"Telegram API error: {e}")
            if e.error_code == 409:  # Conflict - другой экземпляр бота уже запущен
                raise
            logger.info("Restarting bot in 10 seconds...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.info("Restarting bot in 30 seconds...")
            time.sleep(30)


if __name__ == '__main__':
    run_bot()