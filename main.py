from telebot import *

bot = telebot.TeleBot('7700264857:AAEPba5738zzogsnjd2nsnxLzmeREOGFQAQ')
bannedList = []

chatID = -4766934090


@bot.message_handler(commands=['start'])
def main(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, f"<em><b>Привет @{message.from_user.username}!</b></em>", parse_mode='html')
    bot.send_message(message.chat.id, f"<em><b>Предлагай свою песню!)\n\nАвтор - Название</b></em>", parse_mode='html')


@bot.message_handler(commands=['mg'])
def main(message):
    if message.from_user.username == 'ghoulyonok':
        bot.send_message(chatID, message)


@bot.message_handler(commands=['chat'])
def main(message):
    if message.from_user.username == 'ghoulyonok':
        bot.send_message(chatID, message.chat.id)


@bot.message_handler(commands=['ban'])
def main(message):
    if message.chat.id == chatID:
        text = message.text.split()
        bannedList.append(text[1][1:])
        bot.send_message(chatID, f"Вы успешно заблокировали пользователя!)")


@bot.message_handler(commands=['banlist'])
def main(message):
    if message.chat.id == chatID:
        bot.send_message(chatID, f"{bannedList}")


@bot.message_handler()
def info(message):
    if not message.from_user.username in bannedList and message.chat.id != -4766934090:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, f"<em><b>Ваша заявка принята!</b></em>", parse_mode='html')
        bot.send_message(chatID,
                         f"<em><b>Новое предложение от @{message.from_user.username}:\n\n{message.text}</b></em>",
                         parse_mode='html')
    elif message.from_user.username in bannedList and not message.chat.id != -4766934090:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, f"<em><b>Вы были заблокированы за нарушение правил!)</b></em>", parse_mode='html')


bot.infinity_polling()
