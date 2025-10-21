from telebot import types
import telebot
bot = telebot.TeleBot('7541681328:AAEULLNi8N1qItvVGmWYxiG_pJbcP5x9KyM')
@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('ул. Львовская, 1В',callback_data='send1'))
    markup.add(types.InlineKeyboardButton('ул. Родионова, 136',callback_data='send2'))
    markup.add(types.InlineKeyboardButton('ул. Костина, 2',callback_data='send3'))
    markup.add(types.InlineKeyboardButton('ул. Большая Печерская, 25/12', callback_data='send4'))
    bot.reply_to(message,'Корпуса ВШЭ в Нижнем Новогороде:', reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    chat_id=callback.message.chat.id
    if callback.data == 'send1':
        bot.send_location(chat_id=chat_id,latitude=56.268073,longitude=43.877199)
    elif callback.data == 'send2':
        bot.send_location(chat_id=chat_id, latitude=56.317420, longitude=44.067364)
    elif callback.data == 'send3':
        bot.send_location(chat_id=chat_id, latitude=56.312329, longitude=43.991175)
    elif callback.data == 'send4':
        bot.send_location(chat_id=chat_id, latitude=56.324923, longitude=43.022054)
bot.polling(none_stop=True)