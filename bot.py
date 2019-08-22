import telebot
from settings import TOKEN
from sdu import login, get_grades, current_gpa
from datetime import datetime
from telebot import types
from db.models import Session, Student

API_TOKEN = TOKEN

bot = telebot.TeleBot(API_TOKEN)

user_dict = {}
grade_dict = {}

NOW = 2019


def add(message):
    print(message)
    db = Session()
    try:
        obj = db.query(Student).filter(Student.user_id == str(message.from_user.id)).one()
        db.close()
        bot.send_message(message.chat.id, "🤷‍♂️ You are already added")
    except Exception:
        user_dict['chat_id'] = message.chat.id
        bot.send_message(message.chat.id, "Hi new user!")
        msg = bot.send_message(message.chat.id, "✍️ Student id:")
        bot.register_next_step_handler(msg, add_id)


def add_id(message):
    try:
        id = message.text.strip()
        user_dict['student_id'] = id
        msg = bot.send_message(message.chat.id, "🔑 Password:")
        bot.register_next_step_handler(msg, add_pwd)
    except Exception as e:
        bot.send_message(message.chat.id, "😱 Ooops!")


def add_pwd(message):
    try:
        pwd = message.text.strip()
        user_dict['password'] = pwd
        res = login(user_dict['student_id'], user_dict['password'])
        if res['status']:
            user_dict['user_id'] = str(message.from_user.id)
            user_dict['chat_id'] = str(message.chat.id)
            user_dict['created'] = datetime.now()
            user_dict['content'] = res['content']
            try:
                db = Session()
                student = Student(**user_dict)
                db.add(student)
                db.commit()
                db.close()
                bot.send_message(message.chat.id, f'✅ You are in system {res["content"]["Name, surname"]}')
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, f'❌ Sorry we have an error')
        else:
            bot.send_message(message.chat.id, '❌ Wrong id or password')
    except Exception as e:
        bot.send_message(message.chat.id, "😱 Ooops!")


@bot.message_handler(commands=['info'])
def info(message):
    try:
        db = Session()
        print(message.from_user.id)
        obj = db.query(Student).filter(Student.user_id == str(message.from_user.id)).one()
        db.close()

        content = obj.content
        text = ''
        text += f'🔸️ Name, surname {content["Name, surname"]}\n'
        text += f'🔸 Advisor: {content["Advisor"]}\n'
        text += f'🔸 Email: {content["Email"]}\n'
        text += f'🔸 Program: {content["Program / Class"]}\n'
        text += f'🔸 Birth date: {content["Birth date"]}\n'
        text += f'🔸 Grant type: {content["Grant type"]}\n'
        bot.send_message(message.chat.id, text, parse_mode="markdown")
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "🙁 You are not in system, add you with /add")


def grades(message):
    try:
        msg = bot.send_message(message.chat.id, "Enter the year")
        bot.register_next_step_handler(msg, grades_next)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😱 Ooops!")


def grades_next(message):
    try:
        grade_dict['year'] = message.text.strip()
        msg = bot.send_message(message.chat.id, "Enter the term(1 or 2)")
        bot.register_next_step_handler(msg, show_grades)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😱 Ooops!")


def show_grades(message):
    try:
        db = Session()
        obj = db.query(Student).filter(Student.user_id == str(message.from_user.id)).one()
        db.close()
        grade_dict['term'] = message.text.strip()
        temp = get_grades(obj.student_id, obj.password, f'{grade_dict["year"]}#{grade_dict["term"]}')
        text = ""
        for t in temp:
            text += f'{t["Subject"]} - {t["midterm1"]} - {t["midterm2"]} - {t["final"]}\n'
        bot.send_message(message.chat.id, text)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😱 Ooops!")


@bot.message_handler(commands=['start'])
def start(message):
    try:
        db = Session()
        print(message.from_user.id)
        obj = db.query(Student).filter(Student.user_id == str(message.from_user.id)).one()
        db.close()
        markup = types.ReplyKeyboardMarkup()

        btn_me = types.KeyboardButton(f'✋Hello {obj.content["Name, surname"]}')
        btn_grades = types.KeyboardButton('⭐️Grades')
        btn_current_gpa = types.KeyboardButton('🤓 Current GPA')
        markup.row(btn_me)
        markup.row(btn_grades)
        markup.row(btn_current_gpa)
        bot.send_message(message.chat.id, "Choose option:", reply_markup=markup)
    except Exception:
        markup = types.ReplyKeyboardMarkup()
        btn_add = types.KeyboardButton('✌️Add me')
        btn_help = types.KeyboardButton('❗️Help me')
        markup.row(btn_add)
        markup.row(btn_help)
        bot.send_message(message.chat.id, "Choose option:", reply_markup=markup)


def gpa(message):
    try:
        db = Session()
        obj = db.query(Student).filter(Student.user_id == str(message.from_user.id)).one()
        db.close()
        bot.send_message(message.chat.id, current_gpa(obj.student_id, obj.password))
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😱 Ooops!")


@bot.message_handler(func=lambda message: True)
def delegate(message):
    if message.text == '✌️Add me':
        add(message)
    if message.text == '⭐️Grades':
        grades(message)
    if message.text == '🤓 Current GPA':
        gpa(message)
    if '✋Hello' in message.text:
        info(message)


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.polling()
