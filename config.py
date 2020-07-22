import os
from flask_sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'S3cRet_K4Y'
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgres://postgres:MY_parol@localhost/posts')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
