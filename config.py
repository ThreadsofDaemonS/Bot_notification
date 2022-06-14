#!/usr/bin/python3
# _*_ coding: utf-8 _*_

# логирование, ошибки, POSETEGRE_SQL, webhook, PyPy

class Config(object):
    URL = 'https://e33e1d67.ngrok.io'
    TOKEN = 'token'  # test_bot
    DEBUG = False                                             # в самом конце изменить
    DB_FILE = "database.vdb"
    DATABASE_FILE = 'db.sqlite'
    SECRET_KEY = 'secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % DATABASE_FILE

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False

    # Flask-Security config
    SECURITY_URL_PREFIX = "/admin"
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "A"

    # Flask-Security URLs, overridden because they don't put a / at the end
    SECURITY_LOGIN_URL = "/login/"
    SECURITY_LOGOUT_URL = "/logout/"
    SECURITY_REGISTER_URL = "/register/"

    SECURITY_POST_LOGIN_VIEW = "/admin/"
    SECURITY_POST_LOGOUT_VIEW = "/admin/"
    #SECURITY_POST_REGISTER_VIEW = "/admin/"

    # Flask-Security features
    # SECURITY_CONFIRMABLE = True # для проверки почты
    SECURITY_TRACKABLE = True
    SECURITY_REGISTERABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False



class ProductionConfig(Config):
    DEBUG = False

class DevelopConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_ECHO = True


