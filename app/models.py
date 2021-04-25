import sqlalchemy
from app.db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from sqlalchemy_serializer import SerializerMixin

from send_mail import send_message


class Users(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String(30), unique=True)
    email = sqlalchemy.Column(sqlalchemy.String(100), unique=True)
    password = sqlalchemy.Column(sqlalchemy.Text)
    verified = sqlalchemy.Column(sqlalchemy.Boolean)
    code = sqlalchemy.Column(sqlalchemy.String(10))
    avatar = sqlalchemy.Column(sqlalchemy.Text)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def send_code(self):
        send_message(self.email, self.code)

    def verify(self):
        self.verified = True

    def get_data(self):
        return [self.id, self.username, self.email, self.password, self.verified, self.code,
                self.avatar]

    def __repr__(self):
        return f'{self.id} {self.username} {self.email} {self.password} {self.verified} ' \
               f'{self.code} {self.avatar}'


class Posts(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.Text)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    post = sqlalchemy.Column(sqlalchemy.Text)
    image = sqlalchemy.Column(sqlalchemy.Text)
    postname = sqlalchemy.Column(sqlalchemy.Text)

    def get_data(self):
        return [self.id, self.username, self.post, self.image, self.postname]

    def __repr__(self):
        return f'{self.id} {self.username} {self.post} {self.image} {self.postname}'


class Comments(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.Text)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    comment_name = sqlalchemy.Column(sqlalchemy.Text)
    comment = sqlalchemy.Column(sqlalchemy.Text)
    postid = sqlalchemy.Column(sqlalchemy.Text)

    def get_data(self):
        return [self.id, self.username, self.comment_name, self.comment, self.postid]

    def __repr__(self):
        return f'[{self.id}, {self.username}, {self.comment_name}, {self.comment}, {self.postid}]'


class Subscribers(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'subscribers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    subscriber = sqlalchemy.Column(sqlalchemy.Text)
    username = sqlalchemy.Column(sqlalchemy.Text)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)

    def get_data(self):
        return [self.id, self.subscriber, self.username]

    def __repr__(self):
        return f'{self.id}, {self.subscriber}, {self.username}'

