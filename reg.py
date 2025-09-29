import telebot
from telebot import types

bot = telebot.TeleBot('8088954048:AAEb7HgHkz9VR6OkoqVQSOS0hUkWORxzk9k')

users = {}



@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    reg1markup = types.InlineKeyboardMarkup()
    regbtn = types.InlineKeyboardButton('Регистрация', callback_data='register')
    reg1markup.add(regbtn)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}. Добро пожаловать в бота-помощника для студентов НИУ ВШЭ. Для начала пройди регистрацию по кнопке ниже', reply_markup=reg1markup)

@bot.callback_query_handler(func = lambda callback: True)
def handle_callbacks(callback):
    user_id = callback.message.from_user.id
    if callback.data == 'register':
        if user_id not in users:
            reg2markup = types.InlineKeyboardMarkup()
            gr1_btn = types.InlineKeyboardButton('1', callback_data='group1')
            gr2_btn = types.InlineKeyboardButton('2', callback_data='group2')
            gr3_btn = types.InlineKeyboardButton('3', callback_data='group3')
            gr4_btn = types.InlineKeyboardButton('4', callback_data='group4')
            gr5_btn = types.InlineKeyboardButton('5', callback_data='group5')
            gr6_btn = types.InlineKeyboardButton('6', callback_data='group6')
            gr7_btn = types.InlineKeyboardButton('7', callback_data='group7')
            reg2markup.row(gr1_btn, gr2_btn, gr3_btn)
            reg2markup.row(gr4_btn, gr5_btn, gr6_btn)
            reg2markup.add(gr7_btn)
            users[user_id] = {
            'group': '1',
            'is_elder': False,
            'deadlines': []
            }
            bot.send_message(callback.message.chat.id, 'Выбери номер группы', reply_markup=reg2markup)
        else: 
            delmarkup = types.InlineKeyboardMarkup()
            delmarkup.add(types.InlineKeyboardButton('удалить мою запись', callback_data='delete_id'))
            bot.send_message(callback.message.chat.id, 'Ты уже зарегестрирован', reply_markup=delmarkup)
    elif callback.data.startswith('group'):
        users[user_id]['group'] = callback.data.replace('group', '')
        bot.send_message(callback.message.chat.id, f'Супер, ты зарегистрирован в группу {callback.data[-1]}')
    elif callback.data == 'delete_id':
        del users[user_id]
        bot.send_message(callback.message.chat.id, 'Твоя запись удалена. Для повторной регистрации нажми /start')

@bot.message_handler(content_types=['text'])
def main(message):
    user_id = message.from_user.id
    if message.text == 'Стать старостой':
        if user_id not in users:
            reg1markup = types.InlineKeyboardMarkup()
            regbtn = types.InlineKeyboardButton('Регистрация', callback_data='register')
            reg1markup.add(regbtn)
            bot.send_message(message.chat.id, 'Сначала зарегестрируйся!', reply_markup=reg1markup)
        else:
            users[user_id]['is_elder'] = True
            bot.send_message(message.chat.id, 'Ты назначен(а) старостой в своей группе', reply_markup=reg1markup)
        

bot.infinity_polling()