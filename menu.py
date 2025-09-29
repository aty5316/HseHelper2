import telebot
from telebot import types

bot = telebot.TeleBot('8088954048:AAEb7HgHkz9VR6OkoqVQSOS0hUkWORxzk9k')

def menu():
    menumarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    do_eld = types.KeyboardButton('Стать старостой')
    schedule = types.KeyboardButton('Расписание')
    ask_eld = types.KeyboardButton('Обратиться к старосте')
    ask_curator = types.KeyboardButton('Обратиться к куратору')
    deadlines = types.KeyboardButton('Список дедлайнов')
    add_deadline = types.KeyboardButton('Добавить дедлайн')

    menumarkup.row(do_eld, schedule, ask_eld, ask_curator)
    menumarkup.row(deadlines, add_deadline)

    return menumarkup

@bot.message_handler(commands = ['start'])
def start(message):
    bot.send_message(message.chat.id, 'Меню', reply_markup=menu())
    # использовать reply_markup=menu() в местах, где нужно вернуться в меню

bot.infinity_polling()