from app.__init__ import db
from werkzeug.security import check_password_hash
from send_mail import send_message


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.Text)
    verified = db.Column(db.Boolean)
    code = db.Column(db.String(10))
    avatar = db.Column(db.Text)

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


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    post = db.Column(db.Text)
    image = db.Column(db.Text)
    postname = db.Column(db.Text)

    def get_data(self):
        return [self.id, self.username, self.post, self.image, self.postname]

    def __repr__(self):
        return f'{self.id} {self.username} {self.post} {self.image} {self.postname}'


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    comment_name = db.Column(db.Text)
    comment = db.Column(db.Text)
    postid = db.Column(db.Text)

    def get_data(self):
        return [self.id, self.username, self.comment_name, self.comment, self.postid]

    def __repr__(self):
        return f'[{self.id}, {self.username}, {self.comment_name}, {self.comment}, {self.postid}]'


class Subscribers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscriber = db.Column(db.Text)
    username = db.Column(db.Text)

    def get_data(self):
        return [self.id, self.subscriber, self.username]

    def __repr__(self):
        return f'{self.id}, {self.subscriber}, {self.username}'

