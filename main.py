import telebot

from telebot import types
import sqlite3
import os
from datetime import datetime

# Токен бота должен храниться в переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '8164553077:AAEfHbGW8aNbaM8-PUFXpPDR_OvDxIxV_ak')
bot = telebot.TeleBot(BOT_TOKEN)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('university_bot.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            group_number INTEGER NOT NULL,
            is_elder BOOLEAN DEFAULT FALSE,
            username TEXT,
            first_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица дедлайнов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deadlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT NOT NULL,
            description TEXT,
            deadline_time TEXT NOT NULL,
            is_general BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    return conn

# Инициализируем базу данных
db_connection = init_db()

# Временное хранилище для состояний пользователей
user_states = {}

class UserState:
    WAITING_FOR_DEADLINE_NAME = 1
    WAITING_FOR_DEADLINE_DESC = 2
    WAITING_FOR_DEADLINE_TIME = 3
    WAITING_FOR_GENERAL_DEADLINE_NAME = 4
    WAITING_FOR_GENERAL_DEADLINE_DESC = 5
    WAITING_FOR_GENERAL_DEADLINE_TIME = 6

def get_user(user_id):
    """Получить данные пользователя из БД"""
    cursor = db_connection.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if user:
        return {
            'user_id': user[0],
            'group_number': user[1],
            'is_elder': bool(user[2]),
            'username': user[3],
            'first_name': user[4]
        }
    return None

def create_user(user_id, group_number, username, first_name, is_elder=False):
    """Создать нового пользователя"""
    cursor = db_connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (user_id, group_number, username, first_name, is_elder)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, group_number, username, first_name, is_elder))
        db_connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def delete_user(user_id):
    """Удалить пользователя"""
    cursor = db_connection.cursor()
    cursor.execute('DELETE FROM deadlines WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    db_connection.commit()

def add_deadline(user_id, name, description, deadline_time, is_general=False):
    """Добавить дедлайн в БД"""
    cursor = db_connection.cursor()
    cursor.execute('''
        INSERT INTO deadlines (user_id, name, description, deadline_time, is_general)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, name, description, deadline_time, is_general))
    db_connection.commit()
    return cursor.lastrowid

def get_user_deadlines(user_id):
    """Получить дедлайны пользователя"""
    cursor = db_connection.cursor()
    cursor.execute('''
        SELECT id, name, description, deadline_time, is_general 
        FROM deadlines 
        WHERE user_id = ? 
        ORDER BY deadline_time
    ''', (user_id,))
    return cursor.fetchall()

def get_group_users(group_number):
    """Получить всех пользователей группы"""
    cursor = db_connection.cursor()
    cursor.execute('SELECT user_id FROM users WHERE group_number = ?', (group_number,))
    return [row[0] for row in cursor.fetchall()]

def delete_deadline(deadline_id, user_id):
    """Удалить дедлайн пользователя"""
    cursor = db_connection.cursor()
    cursor.execute('DELETE FROM deadlines WHERE id = ? AND user_id = ?', (deadline_id, user_id))
    db_connection.commit()
    return cursor.rowcount > 0

def menu(user_id):
    """Создать меню в зависимости от роли пользователя"""
    menumarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    user = get_user(user_id)
    if user and user['is_elder']:
        add_general_deadline = types.KeyboardButton('Добавить общий дедлайн')
        deadlines = types.KeyboardButton('Список дедлайнов')
        add_deadline = types.KeyboardButton('Добавить дедлайн')
        time_table = types.KeyboardButton('Расписание')
        contact = types.KeyboardButton('Важное')
        buildings = types.KeyboardButton('Корпуса')
        menumarkup.row(add_general_deadline)
        elder = types.KeyboardButton('Староста')
        menumarkup.row(deadlines, add_deadline,time_table,contact,buildings,elder)
    else:
        deadlines = types.KeyboardButton('Список дедлайнов')
        add_deadline = types.KeyboardButton('Добавить дедлайн')
        time_table = types.KeyboardButton('Расписание')
        contact = types.KeyboardButton('Важное')
        buildings = types.KeyboardButton('Корпуса')
        elder = types.KeyboardButton('Староста')
        menumarkup.add(deadlines, add_deadline,time_table,contact,buildings,elder)

    return menumarkup

def validate_date(date_string):
    """Проверка корректности формата даты"""
    try:
        datetime.strptime(date_string, '%d.%m.%Y %H.%M')
        return True
    except ValueError:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start"""
    user_id = str(message.from_user.id)
    user = get_user(user_id)

    if user:
        # Пользователь уже зарегистрирован
        delmarkup = types.InlineKeyboardMarkup()
        del_btn = types.InlineKeyboardButton('Удалить мою запись', callback_data='delete_id')
        menu_btn = types.InlineKeyboardButton('Меню', callback_data='menu')
        delmarkup.row(del_btn, menu_btn)
        bot.send_message(
            message.chat.id,
            f'Привет, {user["first_name"]}! Ты уже зарегистрирован(а) в группе {user["group_number"]}.',
            reply_markup=delmarkup
        )
    else:
        # Новая регистрация
        reg1markup = types.InlineKeyboardMarkup()
        regbtn = types.InlineKeyboardButton('Регистрация', callback_data='register')
        reg1markup.add(regbtn)
        bot.send_message(
            message.chat.id,
            f'Привет, {message.from_user.first_name}. Добро пожаловать в бота-помощника для студентов НИУ ВШЭ. '
            'Для начала пройди регистрацию по кнопке ниже',
            reply_markup=reg1markup
        )

@bot.callback_query_handler(func=lambda callback: True)
def handle_callbacks(callback):
    """Обработчик callback-запросов"""
    user_id = str(callback.from_user.id)

    if callback.data == 'register':
        reg2markup = types.InlineKeyboardMarkup()
        groups = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
                 ('5', '5'), ('6', '6'), ('7', '7')]

        # Создаем кнопки для выбора группы
        buttons = [types.InlineKeyboardButton(text, callback_data=f'group{data}')
                  for data, text in groups]

        # Распределяем кнопки по рядам
        for i in range(0, len(buttons), 3):
            reg2markup.row(*buttons[i:i+3])

        bot.send_message(callback.message.chat.id, 'Выбери номер группы', reply_markup=reg2markup)

    elif callback.data.startswith('group'):
        group_number = callback.data.replace('group', '')

        # Создаем пользователя (старостой назначается только пользователь с определенным ID)
        is_elder = (user_id == '5732022770')  # В реальном приложении это должно быть в конфиге

        success = create_user(
            user_id=user_id,
            group_number=group_number,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            is_elder=is_elder
        )

        if success:
            bot.send_message(
                callback.message.chat.id,
                f'Супер, ты зарегистрирован(а) в группу {group_number}',
                reply_markup=menu(user_id)
            )
        else:
            bot.send_message(callback.message.chat.id, 'Ошибка при регистрации. Попробуйте снова.')

    elif callback.data == 'delete_id':
        delete_user(user_id)
        bot.send_message(
            callback.message.chat.id,
            'Твоя запись удалена. Для повторной регистрации нажми /start'
        )

    elif callback.data == 'menu':
        bot.send_message(callback.message.chat.id, 'Меню', reply_markup=menu(user_id))

    elif callback.data == 'confirm_general_deadline':
        user = get_user(user_id)
        if user and user['is_elder']:
            # Сохраняем временные данные
            temp_data = user_states.get(user_id, {})
            name = temp_data.get('name', '')
            desc = temp_data.get('desc', '')
            time = temp_data.get('time', '')

            if name and desc and time:
                # Добавляем дедлайн всем пользователям группы
                group_users = get_group_users(user['group_number'])
                for group_user_id in group_users:
                    bot.send_message(group_user_id, f'Новый дедлайн!\nНазвание: {name}\nОписание: {desc}\nСрок: {time}')
                    add_deadline(group_user_id, name, desc, time, is_general=True)

                # Очищаем временные данные
                if user_id in user_states:
                    del user_states[user_id]

                bot.send_message(
                    callback.message.chat.id,
                    'Дедлайн отправлен твоим одногруппникам!',
                    reply_markup=menu(user_id)
                )
            else:
                bot.send_message(callback.message.chat.id, 'Ошибка: данные дедлайна не найдены.')
        else:
            bot.send_message(callback.message.chat.id, 'У вас нет прав для этой операции.')

    elif callback.data == 'confirm_deadline':
        temp_data = user_states.get(user_id, {})
        name = temp_data.get('name', '')
        desc = temp_data.get('desc', '')
        time = temp_data.get('time', '')

        if name and time:
            add_deadline(user_id, name, desc, time)

            # Очищаем временные данные
            if user_id in user_states:
                del user_states[user_id]

            bot.send_message(callback.message.chat.id, 'Дедлайн записан!', reply_markup=menu(user_id))
        else:
            bot.send_message(callback.message.chat.id, 'Ошибка: данные дедлайна неполные.')


@bot.message_handler(content_types=['text'])
def commands(message):
    """Обработчик текстовых команд"""
    user_id = str(message.from_user.id)
    user = get_user(user_id)

    if not user:
        bot.send_message(message.chat.id, 'Сначала зарегистрируйтесь с помощью /start')
        return

    # Если пользователь находится в состоянии ввода данных, обрабатываем в handle_user_states
    if user_id in user_states:
        handle_user_states(message, user_id)
        return

    # Обработка дней недели для расписания
    days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    if message.text in days_of_week:
        get_user_text(message)
        return

    street = ['ул. Львовская, 1В', 'ул. Родионова, 136', 'ул. Костина, 2', 'ул. Большая Печерская, 25/12']
    if message.text in street:
        callback_message(message)
        return

    if message.text == 'Назад в меню':
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=menu(user_id))
        return

    if message.text == 'Добавить общий дедлайн':
        if user['is_elder']:
            bot.send_message(message.chat.id, 'Напиши название дедлайна')
            user_states[user_id] = {'state': UserState.WAITING_FOR_GENERAL_DEADLINE_NAME}
        else:
            bot.send_message(message.chat.id, 'У вас нет прав для добавления общих дедлайнов')

    elif message.text == 'Список дедлайнов':
        deadlines = get_user_deadlines(user_id)
        if deadlines:
            response = "📅 Ваши дедлайны:\n\n"
            for i, (deadline_id, name, desc, time, is_general) in enumerate(deadlines, 1):
                general_flag = " (Общий)" if is_general else ""
                response += f"{i}. {name}{general_flag}\n"
                if desc:
                    response += f"   Описание: {desc}\n"
                response += f"   Срок: {time}\n\n"

            response += "Чтобы удалить дедлайн, отправьте его номер"
            bot.send_message(message.chat.id, response)
            user_states[user_id] = {'state': 'waiting_for_deadline_delete'}
        else:
            bot.send_message(message.chat.id, 'У вас пока нет дедлайнов')

    elif message.text == 'Добавить дедлайн':
        bot.send_message(message.chat.id, 'Напиши название дедлайна')
        user_states[user_id] = {'state': UserState.WAITING_FOR_DEADLINE_NAME}

    elif message.text == 'Важное':
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

    elif message.text == 'Расписание':
        show_schedule_menu(message)
    elif message.text == 'Корпуса':
        main(message)
    elif message.text == 'Староста':
        bot.send_message(message.chat.id, 'Напишите в этот чат: @st25cst6_bot')

    # Убрал блок else, так как все состояния теперь обрабатываются в начале функции


def handle_user_states(message, user_id):
    """Обработка состояний пользователя при добавлении дедлайнов"""
    if user_id not in user_states:
        return

    state_data = user_states[user_id]
    state = state_data.get('state')

    if state == UserState.WAITING_FOR_DEADLINE_NAME:
        state_data['name'] = message.text
        state_data['state'] = UserState.WAITING_FOR_DEADLINE_DESC
        bot.send_message(message.chat.id, 'Напиши описание дедлайна')

    elif state == UserState.WAITING_FOR_DEADLINE_DESC:
        state_data['desc'] = message.text
        state_data['state'] = UserState.WAITING_FOR_DEADLINE_TIME
        bot.send_message(message.chat.id, 'Напиши срок дедлайна в формате ДД.ММ.ГГГГ ЧЧ.ММ')

    elif state == UserState.WAITING_FOR_DEADLINE_TIME:
        if validate_date(message.text):
            state_data['time'] = message.text
            show_deadline_confirmation(message.chat.id, user_id, state_data, is_general=False)
        else:
            bot.send_message(message.chat.id, 'Неверный формат даты. Используйте: ДД.ММ.ГГГГ ЧЧ.ММ')

    elif state == UserState.WAITING_FOR_GENERAL_DEADLINE_NAME:
        state_data['name'] = message.text
        state_data['state'] = UserState.WAITING_FOR_GENERAL_DEADLINE_DESC
        bot.send_message(message.chat.id, 'Напиши описание дедлайна')

    elif state == UserState.WAITING_FOR_GENERAL_DEADLINE_DESC:
        state_data['desc'] = message.text
        state_data['state'] = UserState.WAITING_FOR_GENERAL_DEADLINE_TIME
        bot.send_message(message.chat.id, 'Напиши срок дедлайна в формате ДД.ММ.ГГГГ ЧЧ.ММ')

    elif state == UserState.WAITING_FOR_GENERAL_DEADLINE_TIME:
        if validate_date(message.text):
            state_data['time'] = message.text
            show_deadline_confirmation(message.chat.id, user_id, state_data, is_general=True)
        else:
            bot.send_message(message.chat.id, 'Неверный формат даты. Используйте: ДД.ММ.ГГГГ ЧЧ.ММ')

    elif state == 'waiting_for_deadline_delete':
        try:
            deadline_number = int(message.text)
            deadlines = get_user_deadlines(user_id)

            if 1 <= deadline_number <= len(deadlines):
                deadline_id = deadlines[deadline_number - 1][0]
                if delete_deadline(deadline_id, user_id):
                    bot.send_message(message.chat.id, f'Дедлайн №{deadline_number} удален!',
                                     reply_markup=menu(user_id))
                else:
                    bot.send_message(message.chat.id, 'Ошибка при удалении дедлайна')
            else:
                bot.send_message(message.chat.id, 'Неверный номер дедлайна')

            # Очищаем состояние
            if user_id in user_states:
                del user_states[user_id]

        except ValueError:
            bot.send_message(message.chat.id, 'Пожалуйста, введите номер дедлайна')
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    item1 = types.KeyboardButton('ул. Львовская, 1В')
    item2 = types.KeyboardButton('ул. Родионова, 136')
    item3 = types.KeyboardButton('ул. Костина, 2')
    item4 = types.KeyboardButton('ул. Большая Печерская, 25/12')
    back_btn = types.KeyboardButton('Назад в меню')


    markup.add(item1, item2, item3, item4,back_btn)

    bot.reply_to(message,'Корпуса ВШЭ в Нижнем Новогороде:', reply_markup=markup)

def callback_message(message):
    chat_id = message.chat.id
    if message.text == 'ул. Львовская, 1В':
        bot.send_location(chat_id=chat_id, latitude =56.268073,longitude=43.877199)
    elif message.text == 'ул. Родионова, 136':
        bot.send_location(chat_id=chat_id,latitude=56.317420, longitude=44.067364)
    elif message.text == 'ул. Костина, 2':
        bot.send_location(chat_id=chat_id,latitude=56.312329, longitude=43.991175)
    elif message.text == 'ул. Большая Печерская, 25/12':
        bot.send_location(chat_id=chat_id,latitude=56.324923, longitude=43.022054)
def show_schedule_menu(message):
    """Показать меню расписания"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    item1 = types.KeyboardButton('Понедельник')
    item2 = types.KeyboardButton('Вторник')
    item3 = types.KeyboardButton('Среда')
    item4 = types.KeyboardButton('Четверг')
    item5 = types.KeyboardButton('Пятница')
    item6 = types.KeyboardButton('Суббота')
    back_btn = types.KeyboardButton('Назад в меню')

    markup.add(item1, item2, item3, item4, item5, item6, back_btn)

    bot.send_message(message.chat.id, 'Выбери день недели для получения расписания:', reply_markup=markup)


def get_user_text(message):
    """Обработка выбора дня недели"""
    if message.text == "Понедельник":
        bot.send_message(message.chat.id,
                         '📅 Понедельник:\n\n'
                         '8:00-9:20 - НПС «Цифровая грамотность» (Ауд.226)\n'
                         '9:30-10:50 - Линейная алгебра и геометрия (Ауд.303)\n'
                         '11:10-12:30 - Дискретная математика (Ауд.302)\n'
                         '13:00-14:20 - Математический анализ (Ауд.304)')
    elif message.text == "Вторник":
        bot.send_message(message.chat.id, '📅 Вторник:\n\n🎉 Нет занятий')
    elif message.text == "Среда":
        bot.send_message(message.chat.id,
                         '📅 Среда:\n\n'
                         '13:00-14:20 - Математический анализ (Ауд. 318)\n'
                         '14:40-16:00 - Дискретная математика (Ауд.323)\n'
                         '16:20-17:40 - Линейная алгебра и геометрия (Ауд.225)')
    elif message.text == "Четверг":
        bot.send_message(message.chat.id,
                         '📅 Четверг:\n\n'
                         '📊 Расписание доступно по ссылке:\n'
                         'https://docs.google.com/spreadsheets/d/1RB9AWtrYm6Y9m8NSy6On7Zk3byws8RonAGBqeneSxOo/edit?gid=23993546#gid=23993546')
    elif message.text == "Пятница":
        bot.send_message(message.chat.id,
                         '📅 Пятница:\n\n'
                         '📌 Для 05.09., 19.09., 03.10., 17.10.:\n'
                         '8:00-9:20 - Программирование на С++ (Ауд.102)\n'
                         '9:30-10:50 - Программирование на С++ (Ауд.102)\n\n'
                         '📌 Для 12.09., 26.09., 10.10., 24.10.:\n'
                         '11:10-12:30 - Программирование на С++ (Ауд.302)\n'
                         '13:00-14:20 - Программирование на С++ (Ауд.302)')
    elif message.text == "Суббота":
        bot.send_message(message.chat.id, '📅 Суббота:\n\n🎉 Нет занятий')
    elif message.text == "Назад в меню":
        user_id = str(message.from_user.id)
        bot.send_message(message.chat.id, 'Возврат в главное меню', reply_markup=menu(user_id))





def show_deadline_confirmation(chat_id, user_id, state_data, is_general=False):
    """Показать подтверждение дедлайна"""
    name = state_data.get('name', '')
    desc = state_data.get('desc', '')
    time = state_data.get('time', '')
    
    deadline_type = "общий" if is_general else "личный"
    callback_data = 'confirm_general_deadline' if is_general else 'confirm_deadline'
    
    conf_markup = types.InlineKeyboardMarkup()
    conf_btn = types.InlineKeyboardButton('Верно', callback_data=callback_data)
    conf_markup.add(conf_btn)
    
    message_text = (
        f"Отлично! Твой {deadline_type} дедлайн:\n"
        f"📝 Название: {name}\n"
        f"📋 Описание: {desc}\n"
        f"⏰ Срок: {time}\n\n"
        f"Все верно?"
    )
    
    bot.send_message(chat_id, message_text, reply_markup=conf_markup)

if __name__ == '__main__':
    print("Бот запущен...")
    try:
        bot.infinity_polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        db_connection.close()