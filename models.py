#!/usr/bin/python
# _*_ coding: utf-8 _*_

from app import db
import datetime as dt


from flask_security import UserMixin, RoleMixin
# Сделай миграции


class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=dt.datetime.now)
    updated = db.Column(db.DateTime, onupdate=dt.datetime.now)

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):  # Пока что как Посада
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return "Роль: %r" % self.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    # confirmed_at = db.Column(db.DateTime()) # для отправки на почту + settings
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return 'Ім\'я: %r, Почта: %r' % self.first_name, self.email

class Workers(db.Model, TimestampMixin): # поделить на юзеров и Робітників

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(140), nullable=False)
    status = db.Column(db.String(60))
    salary = db.Column(db.Integer, nullable=False)  # зарплатня
    phone_number = db.Column(db.VARCHAR(20), nullable=False, unique=True)
    authorized_in_bot = db.Column(db.Boolean, nullable=False, default=False)
    chat_id = db.Column(db.Integer, nullable=False, unique=True)
    username = db.Column(db.String(60), nullable=False, unique=True)
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(60))
    vacation = db.Column(db.DateTime) # відпустка в днях(Коли закінчується)
    fine_count = db.Column(db.Integer, default=0) # очки штрафу


    #  relationships
    # act = db.relationship('History', backref=db.backref('workers', lazy=True))
    report = db.relationship('Reports', backref=db.backref('workers', lazy=True))
    fine = db.relationship('Fines', backref=db.backref('workers', lazy=True))


    def __repr__(self):
        return 'ПІП: %r' % self.fullname #поменять на fullname


# class History(db.Model):  # щось схоже на історію
#
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     date = db.Column(db.DateTime, nullable=False, default=dt.datetime.now)
#     act = db.Column(db.String(255), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#
#     def __repr__(self):
#         return 'Дія: %r' % self.act


class Reports(db.Model, TimestampMixin):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)


    def __repr__(self):
        return 'Звіт: %r' % self.report


class Fines(db.Model, TimestampMixin):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fine = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)


    def __repr__(self):
        return 'Штраф: %r' % self.fine

class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String)
    answer = db.Column(db.String)

class Salary(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String)
    answer = db.Column(db.String)



