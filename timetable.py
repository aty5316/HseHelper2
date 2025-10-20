import telebot
from telebot import types

bot = telebot.TeleBot('8410733822:AAHdw5HaFH-7x5aoWH7PBDE-6mUbluF3R_8')
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    item1 = types.KeyboardButton('Понедельник')
    item2 = types.KeyboardButton('Вторник')
    item3 = types.KeyboardButton('Среда')
    item4 = types.KeyboardButton('Четверг')
    item5 = types.KeyboardButton('Пятница')
    item6 = types.KeyboardButton('Суббота')

    markup.add(item1, item2, item3, item4, item5, item6)

    bot.send_message(message.chat.id,'Привет! Выбери день недели для получения расписания.', reply_markup=markup)

@bot.message_handler()
def get_user_text(message):
    if message.text == "Понедельник":
        bot.send_message(message.chat.id, '8:00-9:20 - НПС «Цифровая грамотность» (Ауд.226)\n9:30-10:50 - Линейная алгебра и геометрия (Ауд.303)\n11:10-12:30 - Дискретная математика (Ауд.302)\n13:00-14:20 - Математический анализ (Ауд.304)', parse_mode='html')
    elif message.text == "Вторник":
        bot.send_message(message.chat.id, 'Нет занятий', parse_mode='html')
    elif message.text == "Среда":
        bot.send_message(message.chat.id, '13:00-14:20 - Математический анализ (Ауд. 318)\n14:40-16:00 - Дискретная математика (Ауд.323)\n16:20-17:40 - Линейная алгебра и геометрия (Ауд.225)', parse_mode='html')
    elif message.text == "Четверг":
        bot.send_message(message.chat.id, 'https://docs.google.com/spreadsheets/d/1RB9AWtrYm6Y9m8NSy6On7Zk3byws8RonAGBqeneSxOo/edit?gid=23993546#gid=23993546', parse_mode='html')
    elif message.text == "Пятница":
        bot.send_message(message.chat.id, '05.09., 19.09., 03.10., 17.10.\n8:00-9:20 - Программирование на С++ (Ауд.102)\n9:30-10:50 - Программирование на С++ (Ауд.102)\n\n12.09., 26.09., 10.10., 24.10.\n11:10-12:30 - Программирование на С++ (Ауд.302)\n13:00-14:20 - Программирование на С++ (Ауд.302)', parse_mode='html')
    elif message.text == "Суббота":
        bot.send_message(message.chat.id, 'Нет занятий', parse_mode='html')


bot.polling(non_stop=True)


