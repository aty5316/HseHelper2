import telebot
from telebot import types
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

bot = telebot.TeleBot('8088954048:AAEb7HgHkz9VR6OkoqVQSOS0hUkWORxzk9k')


users = {
    '1184286159' : {
        'group': '6',
        'is_elder': True,
        'deadlines': []
    }
}
new_deadline = {}

class ElderStates(StatesGroup):
    deadline_title = State()
    deadline_description = State()
    deadline_time = State()

def menu(user_id):
    menumarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    add_general_deadline = types.KeyboardButton('Добавить общий дедлайн')
    schedule = types.KeyboardButton('Расписание')
    ask_eld = types.KeyboardButton('Обратиться к старосте')
    ask_curator = types.KeyboardButton('Обратиться к куратору')
    deadlines = types.KeyboardButton('Список дедлайнов')
    add_deadline = types.KeyboardButton('Добавить дедлайн')
    if user_id in users.keys() and users[user_id]['is_elder']:
        menumarkup.row(add_general_deadline, schedule, ask_eld, ask_curator)
        menumarkup.row(deadlines, add_deadline)
    else:
        menumarkup.row(schedule, ask_eld, ask_curator)
        menumarkup.row(deadlines, add_deadline)
    return menumarkup

@bot.message_handler(commands=['start'])
def start(message):
    reg1markup = types.InlineKeyboardMarkup()
    regbtn = types.InlineKeyboardButton('Регистрация', callback_data='register')
    reg1markup.add(regbtn)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}. Добро пожаловать в бота-помощника для студентов НИУ ВШЭ. Для начала пройди регистрацию по кнопке ниже', reply_markup=reg1markup)

@bot.callback_query_handler(func = lambda callback: True)
def handle_callbacks(callback):
    user_id = str(callback.from_user.id)
    if callback.data == 'register':
        if user_id not in users.keys():
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
            del_btn = types.InlineKeyboardButton('удалить мою запись', callback_data='delete_id')
            menu_btn = types.InlineKeyboardButton('Меню', callback_data='menu')
            delmarkup.row(del_btn, menu_btn)
            bot.send_message(callback.message.chat.id, 'Ты уже зарегистрирован(а)', reply_markup=delmarkup)
    elif callback.data.startswith('group'):
        users[user_id]['group'] = callback.data.replace('group', '')
        bot.send_message(callback.message.chat.id, f'Супер, ты зарегистрирован(а) в группу {callback.data[-1]}', reply_markup = menu(user_id))
    elif callback.data == 'delete_id':
        del users[user_id]
        bot.send_message(callback.message.chat.id, 'Твоя запись удалена. Для повторной регистрации нажми /start')
    elif callback.data == 'menu':
        bot.send_message(callback.message.chat.id, 'Меню', reply_markup = menu(user_id))
    elif callback.data == 'confirm_general_deadline':
        bot.send_message(callback.message.chat.id, 'Отправляю дедлайн твоим одногруппникам')
        for user_id in users.keys():
            bot.send_message(user_id, f"Новый дедлайн!\nНазвание: {new_deadline['name']}\nОписание: {new_deadline['desc']}\nСрок: {new_deadline['time']}")
            users[user_id]['deadlines'].add(new_deadline)
            new_deadline.clear()

@bot.message_handler(content_types=['text'])
def add_general_deadline(message):
    if message.text == 'Добавить общий дедлайн':
        bot.send_message(message.chat.id, 'Напиши название дедлайна')
        bot.register_next_step_handler(message, deadline_desc)

def deadline_desc(message):
    new_deadline['name'] = message.text
    bot.send_message(message.chat.id, 'Напиши описание дедлайна')
    bot.register_next_step_handler(message, deadline_time)

def deadline_time(message):
    new_deadline['desc'] = message.text
    bot.send_message(message.chat.id, 'Напиши срок дедлайна в формате ДД.ММ.ГГГГ ЧЧ.ММ')
    bot.register_next_step_handler(message, deadline_confirm)

def deadline_confirm(message):
    new_deadline['time'] = message.text
    conf_markup = types.InlineKeyboardMarkup()
    conf_btn = types.InlineKeyboardButton('Верно', callback_data = 'confirm_general_deadline')
    conf_markup.add(conf_btn)
    bot.send_message(message.chat.id, f"Отлично твой дедлайн:\nНазвание: {new_deadline['name']}\nОписание: {new_deadline['desc']}\nСрок: {new_deadline['time']}\nВсе верно?", reply_markup=conf_markup)

bot.infinity_polling()