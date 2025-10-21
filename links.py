import telebot

bot = telebot.TeleBot('7810419849:AAHAAGMZVQWCGXUnDQ0K5JHDHHWIgzlzDqw')

@bot.message_handler(commands=['start'])
def main(message):
    text = (
        "📚 <b>Полезные ссылки ВШЭ:</b>\n\n"
        "🌐 <a href='https://www.hse.ru/'>Сайт ВШЭ</a>\n"
        "📧 <a href='https://mail.yandex.ru/'>Яндекс 360 / почта студента</a>\n"
        "💻 <a href='http://lms.hse.ru/'>LMS</a>\n"
        "🧠 <a href='https://edu.hse.ru/'>SmartLMS</a>\n"
        "👤 <a href='https://lk.hse.ru/'>SmartPoint (личный кабинет)</a>\n"
        "📱 <a href='https://apps.apple.com/ru/app/hse-app-x/id1527320487'>HSE App X (iOS)</a> | "
        "<a href='https://play.google.com/store/apps/details?id=com.hse.app2&hl=ru&gl=US'>Android</a>\n"
        "📘 <a href='https://www.hse.ru/edu/courses/'>Учебные курсы</a>\n"
        "📊 <a href='https://www.hse.ru/org/hse/elective_courses/'>Выбор траектории обучения</a>\n"
        "📨 <a href='https://www.hse.ru/news/'>Новости</a>\n"
        "📅 <a href='https://www.hse.ru/announcements/'>Календарь мероприятий</a>\n"
        "🧾 <a href='https://antiplagiat.ru/'>Антиплагиат</a>\n"
        "🏖 <a href='https://www.hse.ru/sumschool/'>Летние школы</a>\n"
        "🗞 <b>Пресс-служба ВШЭ НН:</b> <a href='mailto:PRnn@hse.ru'>PRnn@hse.ru</a>\n"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML')

bot.polling(non_stop=True)
