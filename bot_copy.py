#!/usr/bin/python3
# _*_ coding: utf-8 _*_

# import requests
from app import db, app, request
from models import Workers, FAQ, Salary, Fines, Reports
import telebot
from telebot import types
from keyboard import Keyboard
import datetime as d

from config import ProductionConfig



bot = telebot.TeleBot(ProductionConfig.TOKEN)
keyboard = Keyboard(bot)

T = d.time(18, 0, 0)
contactus = """
Ласкаво просимо
Привіт, вас вітає компанія "Організація"!
Яка займається, щоб ви подумали - правильно - організацією!

Ось наші контакти:
Call-center: 383-383-383 
Наш сайт: www.OOO_Organizaciya.com
"""

# Создание ежедневной записи в бд с пуcтым полем самого отчета (ускорене всего)


def notification():
    users = Workers.query.all()
    for user in users:
        if None in [r.report for r in user.report]:
            bot.send_message(user.chat_id, 'Здайте будь-ласка звіт!')

def create_report():
    users = Workers.query.all()
    for user in users:
        DATE = [(user.created + d.timedelta(day)).date() for day in range(((d.datetime.now() - user.created).days + 1))]
        for date in DATE:
            if date not in [r.created.date() for r in user.report]:
                r = Reports(report=None, created=date)
                user.report.append(r)
                db.session.add(user)
                db.session.commit()
        else:
            reprt = Reports.query.filter(Reports.user_id == user.id).order_by(Reports.created).all()
            if reprt[-1].created.date() != d.datetime.now().date():
                r = Reports(report=None)
                user.report.append(r)
                db.session.add(user)
                db.session.commit()


@bot.message_handler(commands=["start"])
def start(msg):
    print(msg)
    bot.send_message(msg.chat.id, 'Роботу з ботом розпочато! Для більш детальної інформації про бота оберіть /about')
    bot.send_message(msg.chat.id, 'Оберіть /verification для авторизації')


@bot.message_handler(commands=["about"])
def about(msg):
    bot.send_message(msg.chat.id, contactus)

@bot.message_handler(commands=["verification"])
def acitvate(msg):
    butn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    butn.add(types.KeyboardButton(text="Авторизуватися", request_contact=True))
    bot.send_message(msg.chat.id, 'Відправте номер телефону', reply_markup=butn)

@bot.message_handler(content_types=['contact'])
def verification(msg):
    fu = msg.from_user
    user = Workers.query.filter_by(chat_id=fu.id).first()
    id = user.chat_id
    pn = user.phone_number
    if msg.contact.user_id == fu.id and id == fu.id and pn == msg.contact.phone_number:
        bot.send_message(msg.chat.id, 'Авторизацію пройдено \nЛаскаво просимо, %s ' % fu.first_name,
                         reply_markup=types.ReplyKeyboardRemove(True))
        bot.send_message(msg.chat.id, "Оберіть пункт:", reply_markup=keyboard.menu())
        user.authorized_in_bot = True
        db.session.add(user)
        db.session.commit()
    else:
        bot.send_message(msg.chat.id, 'Авторизацію не пройдено')


@bot.callback_query_handler(func=lambda call: call.message.from_user.id == 461457277 and \
                                              Workers.query.filter_by(chat_id=call.message.chat.id).first().authorized_in_bot) # id бота
def callback_menu(call):
    user = Workers.query.filter_by(chat_id=call.message.chat.id).first()
    reprt = Reports.query.filter(Reports.user_id == user.id).order_by(Reports.created).all()
    faq = FAQ.query.all()
    sal = Salary.query.all()
    if call.message:
        if call.data == 'report_menu':
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboard.report_menu())
        elif call.data == 'report':
            for r in user.report:
                if r.report == None and r.created.date() != d.datetime.now().date():
                    score = 24
                    fine = 'Штраф: %d балли - запізнення зі звітом на 1 день за %s' % (score, r.created.strftime("%d.%m.%Y"))
                    f = Fines(fine=fine, created=r.created)
                    user.fine_count += score
                    user.fine.append(f)
                    user.salary -= user.fine_count # Проверить
                    db.session.add(user)
                    db.session.commit()
                    to_report = 'Наберіть звіт за %s:' % r.created.strftime("%d.%m.%Y")
                    bot.send_message(call.message.chat.id, text=to_report)
                    bot.register_next_step_handler(call.message, report)
                    break
                else:
                    if d.datetime.now().time() > T:
                        score = d.datetime.now().hour - T.hour
                        fine = 'Штраф: %d баллів - запізнення зі звітом на %d год.' % (score, score)
                        f = Fines(fine=fine)
                        user.fine_count += score
                        user.fine.append(f)
                        user.salary -= user.fine_count
                        db.session.add(user)
                        db.session.commit()
                    bot.send_message(call.message.chat.id, 'Наберіть ваш звіт:')
                    bot.register_next_step_handler(call.message, report)


        elif call.data == 'edit_report':
            if user.report:
                if reprt[-1].created.date() == d.datetime.now().date():
                    bot.send_message(call.message.chat.id, 'Ось що ви відправили:\n%s\n\nНапишіть тут що має бути:' \
                                     % reprt[-1].report)
                    bot.register_next_step_handler(call.message, edit_report)
                else:
                    bot.send_message(call.message.chat.id, 'Редагувати можна тільки звіт за сьогодні')
                    bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.report_menu())
            else:
                bot.send_message(call.message.chat.id, 'У вас немає звітів.')
                bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.report_menu())

        elif call.data == 'menu':
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboard.menu())

        elif call.data == 'fines':
            msg_text = ''
            for fine in user.fine[:20]:
                msg_text += fine.fine + '\n'
            bot.send_message(call.message.chat.id, text=msg_text)
            bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.menu())

        elif call.data == 'profile':
            vac = 0
            if user.vacation:
                vac = (user.vacation - d.datetime.now()).days
            text = 'Співробітник: %s\nПосада: %s\nДата початку роботи: %s\nПроробив в компанії: %s\nЗалишок відпустки: %s\nЗарплатня:%s'\
                   % (user.fullname, user.status, user.created.date().strftime("%d.%m.%Y"),
                           (d.datetime.now() - user.created).days, vac, user.salary)
            bot.send_message(call.message.chat.id, text=text)
            bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.menu())

        elif call.data == 'questions':
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboard.questions())

        elif call.data == 'allquestions':
            markup = types.InlineKeyboardMarkup(row_width=1)
            for q in faq:
                markup.add(types.InlineKeyboardButton(text=q.question, callback_data=q.question))
            Back = types.InlineKeyboardButton(text="Назад", callback_data="questions")
            markup.add(Back)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup)

        elif call.data == 'salary':
            markup = types.InlineKeyboardMarkup(row_width=1)
            for q in sal:
                markup.add(types.InlineKeyboardButton(text=q.question, callback_data=q.question))
            Back = types.InlineKeyboardButton(text="Назад", callback_data="questions")
            markup.add(Back)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup)

        elif call.data in [e.question for e in faq]:
            for a in faq:
                if call.data == a.question:
                    bot.send_message(call.message.chat.id, text=a.answer)
                    bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.questions())

        elif call.data in [e.question for e in sal]:
            for a in sal:
                if call.data == a.question:
                    bot.send_message(call.message.chat.id, text=a.answer)
                    bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.questions())

def report(msg): # проверка по бд и т.д.
    if msg.content_type == 'text': # как записывать отчеты в бд
        user = Workers.query.filter_by(chat_id=msg.chat.id).first()
        for r in user.report:
            if r.report == None:
                r.report = msg.text
                break
        db.session.add(user)
        db.session.commit()
        bot.send_message(msg.chat.id, "Оберіть пункт:", reply_markup=keyboard.report_menu())
    else:
        bot.send_message(msg.chat.id, "Введіть будь-ласка текст!")
        bot.register_next_step_handler(msg, report)

def edit_report(msg):
    if msg.content_type == 'text':
        user = Workers.query.filter_by(chat_id=msg.chat.id).first()
        reprt = Reports.query.filter(Reports.user_id == user.id).order_by(Reports.created).all()
        reprt[-1].report = msg.text
        db.session.add(user)
        db.session.commit()
        bot.send_message(msg.chat.id, "Меню", reply_markup=keyboard.report_menu())
    else:
        bot.send_message(msg.chat.id, "Введіть будь-ласка текст!")
        bot.register_next_step_handler(msg, edit_report())

@bot.message_handler(commands=["menu"])
@bot.message_handler(func=lambda msg: Workers.query.filter_by(chat_id=msg.chat.id).first().authorized_in_bot)
def menu_r(msg):
    bot.send_message(msg.chat.id, "Оберіть пункт:", reply_markup=keyboard.menu())


@app.route("/{}".format(ProductionConfig.TOKEN), methods=['POST'])
def getMessage():
    bot.process_new_updates([types.Update.de_json(request.data.decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="{}/{}".format(ProductionConfig.URL, ProductionConfig.TOKEN))
    return "!", 200