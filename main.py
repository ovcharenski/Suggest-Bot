import csv

from telebot import *

bot = telebot.TeleBot('8334964606:AAGw0r4NYXZ-fHFoj7MZOvcB0GIEdNeubiE')
adminChatId = -1001953854909


def readcsv(listname):
    diction = {}
    filename = {
        "admin": "adminList.csv",
        "banned": "bannedList.csv",
        "reg": "regList.csv"
    }.get(listname, "NotFound")

    try:
        # Явно указываем кодировку utf-8 при открытии файла
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for line in reader:
                if not line or line[0] == "username":  # Пропускаем пустые строки и заголовок
                    continue
                try:
                    diction[line[0]] = [line[1], int(line[2])]
                except (IndexError, ValueError) as e:
                    print(f"Ошибка обработки строки: {line}. Ошибка: {e}")
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

    return diction


def changecsv(listname, mg):
    filename = {
        "admin": "adminList.csv",
        "banned": "bannedList.csv",
        "reg": "regList.csv"
    }.get(listname, "NotFound")

    try:
        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([mg.from_user.username, mg.from_user.first_name, mg.from_user.id])
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")


def adduser(listname, username):
    filename = {
        "admin": "adminList.csv",
        "banned": "bannedList.csv",
        "reg": "regList.csv"
    }.get(listname, "NotFound")

    try:
        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, 0, 0])
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")


def deluser(listname, username):
    filename = {
        "admin": "adminList.csv",
        "banned": "bannedList.csv",
        "reg": "regList.csv"
    }.get(listname, "NotFound")

    try:
        # Удаляем из файла
        with open(filename, 'r', encoding='utf-8') as file:
            rows = list(csv.reader(file))

        # Фильтруем строки (удаляем строку с нужным ID)
        filtered_rows = [row for row in rows if row[0] != username]

        # Перезаписываем файл
        with open(filename, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(filtered_rows)
    except Exception as e:
        print(f"Ошибка: {e}")


@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.username not in readcsv("reg"):
        changecsv("reg", message)

    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, f"<em><b>Привет @{message.from_user.username}!</b></em>", parse_mode='html')
    bot.send_message(message.chat.id, f"<em><b>Предлагай свою песню!)\n\nАвтор - Название</b></em>", parse_mode='html')


@bot.message_handler(commands=['info'])
def getinfo(message):
    if message.from_user.username in readcsv("admin"):
        if message.reply_to_message:
            original_message_user = message.reply_to_message.from_user
            bot.send_message(message.chat.id, f"@{original_message_user.username}\n"
                                              f"{original_message_user.first_name}\n"
                                              f"ID: <code>{original_message_user.id}</code>", parse_mode='html')
        elif "@" in message.text:
            user = message.text.split()[1][1:]
            if user in readcsv("reg"):
                bot.send_message(message.chat.id, f"@{user}\n"
                                                  f"{readcsv("reg")[user][0]}\n"
                                                  f"ID: <code>{readcsv("reg")[user][1]}</code>", parse_mode='html')
            else:
                bot.reply_to(message, f"Error 101: UserNotFound")
        else:
            bot.send_message(message.chat.id, f"@{message.from_user.username}\n"
                                              f"{message.from_user.first_name}\n"
                                              f"ID: <code>{message.from_user.id}</code>", parse_mode='html')


@bot.message_handler(commands=['id'])
def getid(message):
    if message.from_user.username in readcsv("admin"):
        if message.reply_to_message:
            original_message = message.reply_to_message
            bot.send_message(message.chat.id, f"ID: <code>{original_message.from_user.id}</code>", parse_mode='html')
        elif "@" in message.text:
            user = message.text.split()[1][1:]
            if user in readcsv("reg"):
                bot.send_message(message.chat.id,f"ID: <code>{readcsv("reg")[user][1]}</code>", parse_mode='html')
            else:
                bot.reply_to(message, f"Error 101: UserNotFound")
        else:
            bot.send_message(message.chat.id, f"ID: <code>{message.from_user.id}</code>", parse_mode='html')


@bot.message_handler(commands=['chat'])
def chat(message):
    if message.from_user.username in readcsv("admin"):
        bot.send_message(message.chat.id, message.chat.id)


@bot.message_handler(commands=['ban'])
def ban(message):
    if message.chat.id == adminChatId and "@" in message.text:
        user = message.text.split()[1][1:]
        adduser("banned", user)
        bot.send_message(adminChatId, f"Вы успешно заблокировали пользователя!")


@bot.message_handler(commands=['unban'])
def unban(message):
    if message.chat.id == adminChatId and "@" in message.text:
        user = message.text.split()[1][1:]
        if user in readcsv("banned"):
            deluser("banned", user)
            bot.send_message(adminChatId, f"Вы успешно разблокировали пользователя!")
        else:
            bot.reply_to(message, f"Error 101: UserNotFound")


@bot.message_handler(commands=['op'])
def op(message):
    if message.chat.id == adminChatId and message.from_user.username == "ghoulyonok" and "@" in message.text:
        if message.reply_to_message:
            original_message = message.reply_to_message
            changecsv("admin", original_message)
            bot.send_message(adminChatId, f"Вы успешно повысили пользователя!")
        else:
            bot.reply_to(message, f"Error 101: UserNotFound")


@bot.message_handler(commands=['unop'])
def unop(message):
    if message.chat.id == adminChatId and message.from_user.username == "ghoulyonok" and "@" in message.text:
        if message.reply_to_message:
            original_message = message.reply_to_message
            user = original_message.from_user.username
        else:
            user = message.text.split()[1][1:]
        if user in readcsv("admin"):
            user_to_kick = readcsv('admin')[user]
            print(user_to_kick)
            bot.kick_chat_member(
                chat_id=adminChatId,
                user_id=user_to_kick[1]
            )
            deluser("admin", user)
            bot.send_message(adminChatId, f"Вы успешно понизили пользователя!")
        else:
            print(user)
            bot.reply_to(message, f"Error 101: UserNotFound")


@bot.message_handler(commands=['banlist'])
def banlist(message):
    if message.chat.id == adminChatId:
        banned_users = readcsv("banned")

        if not banned_users:
            bot.send_message(message.chat.id, "Список забаненных пуст")
            return

        # Формируем красивое сообщение
        message_text = "🤬 <b>BAN LIST</b> 🤬\n\n"
        for idx, (username, user_data) in enumerate(banned_users.items(), 1):
            message_text += (
                f"{idx}. @{username}\n"
                f"    {user_data[0]}\n"
                f"    ID: <code>{user_data[1]}</code>\n\n"
            )

        # Отправка с HTML-разметкой
        bot.send_message(
            chat_id=message.chat.id,
            text=message_text,
            parse_mode='HTML',
            disable_web_page_preview=True
        )


@bot.message_handler(commands=['adminlist'])
def adminlist(message):
    if message.chat.id == adminChatId:
        admin_users = readcsv("admin")

        if not admin_users:
            bot.send_message(message.chat.id, "Список забаненных пуст")
            return

        # Формируем красивое сообщение
        message_text = "✨ <b>ADMIN LIST</b> ✨\n\n"
        for idx, (username, user_data) in enumerate(admin_users.items(), 1):
            message_text += (
                f"{idx}. @{username}\n"
                f"    {user_data[0]}\n"
                f"    ID: <code>{user_data[1]}</code>\n\n"
            )

        # Отправка с HTML-разметкой
        bot.send_message(
            chat_id=message.chat.id,
            text=message_text,
            parse_mode='HTML',
            disable_web_page_preview=True
        )


@bot.message_handler()
def info(message):
    if message.chat.id != adminChatId and message.from_user.username not in readcsv("admin"):
       if message.from_user.username in readcsv("banned"):
           bot.send_chat_action(message.chat.id, 'typing')
           bot.send_message(message.chat.id, f"<em><b>Вы были заблокированы за нарушение правил!</b></em>", parse_mode='html')

       else:
           bot.send_chat_action(message.chat.id, 'typing')
           bot.send_message(message.chat.id, f"<em><b>Ваша заявка принята!</b></em>", parse_mode='html')
           bot.send_message(adminChatId, f"<em><b>Новое предложение от @{message.from_user.username}:\n\n{message.text}</b></em>", parse_mode='html')


if __name__ == '__main__':
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Ошибка в работе бота: {e}")