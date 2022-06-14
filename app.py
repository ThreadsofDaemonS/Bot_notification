#!/usr/bin/python
# _*_ coding: utf-8 _*_

# logging, issuses, test
import datetime as d

from flask import Flask, request, session, redirect, abort, url_for
from flask_sqlalchemy import SQLAlchemy


from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore, current_user

from flask_admin import helpers as admin_helpers

from config import ProductionConfig
from flask_babelex import Babel

app = Flask(__name__)
app.config.from_object(ProductionConfig)
babel = Babel(app)


@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'uk')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


from models import *
admin = Admin(app, name='WEB-консоль', base_template='my_master.html', template_mode='bootstrap3')

class RoleUsersModelView(ModelView):
    can_view_details = True
    column_exclude_list = ['password', ]
    form_excluded_columns = ['last_login_at', 'current_login_at', 'last_login_ip', 'current_login_ip', 'login_count']

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False


    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

# class HistoryModelView(ModelView, RoleUsersModelView):
#     column_labels = {'date': 'Коли', 'act': 'Дія', 'users': 'Робітник'}

class WorkersModelView(RoleUsersModelView):
    column_labels = {'fullname': 'ПІП', 'status': 'Посада', 'salary': 'Зарплатня',
                     'phone_number': 'Номер телефону', 'authorized_in_bot': 'Авторизован',
                     'vacation': 'Відпустка', 'fine_count': 'Штрафні бали'}
    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('user'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True

        if current_user.has_role('superuser'):
            return True

        return False

class ReportsModelView(RoleUsersModelView): # створення один раз за день, доступ до всього тільки у однієї особи
    column_labels = {'created': 'Створено', 'updated': 'Останнє оновлення', 'report': 'Звіт', 'users': 'Робітник'}
    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('user'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True

        if current_user.has_role('superuser'):
            return True

        return False

    # can_create = False
    # can_edit = False
    # can_delete = False

class FinesModelView(RoleUsersModelView):
    column_labels = {'created': 'Створено', 'updated': 'Останнє оновлення', 'fine': 'Штраф', 'users': 'Робітник'}
    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('user'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True

        if current_user.has_role('superuser'):
            return True

        return False


class InfoModelView(RoleUsersModelView):
    column_labels = {'question': 'Питання', 'answer': 'Відповідь'}
    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('user'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True

        if current_user.has_role('superuser'):
            return True

        return False


# admin.add_view(RoleUsersModelView(Role, db.session))
admin.add_view(RoleUsersModelView(User, db.session))
admin.add_view(WorkersModelView(Workers, db.session, name='Робітники'))
# admin.add_view(HistoryModelView(History, db.session, name='Журнал'))
admin.add_view(ReportsModelView(Reports, db.session, name='Звіти'))
admin.add_view(FinesModelView(Fines, db.session, name='Штрафи'))
admin.add_view(InfoModelView(FAQ, db.session, name='Загальні питання'))
admin.add_view(InfoModelView(Salary, db.session, name='Питання по зарплатні'))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

#test for all system

from flask_security.utils import hash_password
db.drop_all()
db.create_all()
with app.app_context():
    date = d.datetime.now().date() - d.timedelta(days=5)
    user_role = Role(name='user')
    super_user_role = Role(name='superuser')
    w = Workers(fullname='Ф І О', status='Адмін', salary=20000,
              phone_number='+yourphonenumber', chat_id=332291910, username='RazDua', first_name='1', last_name='2', created=date)
    db.session.add(user_role)
    db.session.add(super_user_role)
    db.session.add(w)
    db.session.commit()
    test_admin = user_datastore.create_user(
        first_name='Admin',
        email='admin',
        password=hash_password('admin'),
        roles=[user_role, super_user_role]
    )
    test_user = user_datastore.create_user(
        first_name='test',
        email='test@example.com',
        password=hash_password('test'),
        roles=[user_role]
    )
    db.session.commit()









#                                                  Замітки
#============================================================================================================

# cron

# как в хэндлере ловить date

# for date in [(user.created.date() + d.timedelta(day)) for day in range(((d.datetime.now() - user.created).days))]:
#     if date not in [r.created.date() for r in user.report]:
#         to_report = 'Спочатку наберіть звіт за %s' % date.strftime("%Y%m%d")
#         bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
#         bot.send_message(call.message.chat.id, text=to_report)
#         bot.register_next_step_handler(call.message, report)
#         break




 # if call.data == 'intro':
        #     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
        #                                   reply_markup=keyboard.intro())
        #
        # elif call.data == 'menu':
        #     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
        #                                   reply_markup=keyboard.menu())
        #
        # elif call.data == 'report_menu':
        #     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
        #                           reply_markup=keyboard.report_menu())

# elif call.data == 'questions':
        #     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
        #                                   reply_markup=keyboard.questions())
        #
        # elif call.data == 'profile':
        #     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
        #                                   reply_markup=keyboard.profile())

#URL = 'https://api.telegram.org/bot%s/getUpdates' % Conf.TOKEN
# while True:
#     try:
#         r = requests.get(url).json()
#         print(r['result'][len(r)-1]['message']['from']['id'])
#         time.sleep(2)
#     except Exception as e:
#         print(e)


# ./ngrok - > https


# def intro(msg):
#     if msg.text == 'Меню':
#         keyboard.menu(msg)
#         tdb.set_state(msg.from_user.id, 'menu')
#     elif msg.text == 'Скласти звіт':
#         keyboard.report(msg)
#         tdb.set_state(msg.from_user.id, 'report')
#     else:
#         bot.register_next_step_handler(msg, intro)
#
# @bot.message_handler(func=lambda msg: tdb.get_current_state(msg.chat.id) == cn.States.S_MENU.value)
# def Menu(msg):
#     if msg.text == 'Назад':
#         keyboard.intro(msg)
#         bot.register_next_step_handler(msg, intro)
#     elif msg.text == 'Питання та відповіді':
#         keyboard.questions(msg)
#         tdb.set_state(msg.from_user.id, 'questions')
#     elif msg.text == 'Профіль':
#         keyboard.profile(msg)
#         tdb.set_state(msg.from_user.id, 'profile')
#
# @bot.message_handler(func=lambda msg: tdb.get_current_state(msg.chat.id) == cn.States.S_REPORT.value)
# def Report(msg):
#     if msg.text == 'Назад':
#         keyboard.intro(msg)
#         bot.register_next_step_handler(msg, intro)
#     elif msg.text == 'Звіт':
#         pass
#
# @bot.message_handler(func=lambda msg: tdb.get_current_state(msg.chat.id) == cn.States.S_QUESTIONS.value)
# def Questions(msg):
#     if msg.text == 'Назад':
#         keyboard.menu(msg)
#         tdb.set_state(msg.from_user.id, 'menu')
#     elif msg.text == 'Загальні питання':
#         pass
#     elif msg.text == 'Питання по зарплатні':
#         pass
#
# @bot.message_handler(func=lambda msg: tdb.get_current_state(msg.chat.id) == cn.States.S_PROFILE.value)
# def Profile(msg):
#     if msg.text == 'Назад':
#         keyboard.menu(msg)
#         tdb.set_state(msg.from_user.id, 'menu')
