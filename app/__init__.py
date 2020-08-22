from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, template_folder='templates')
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdTCbQZAAAAAOSVAPFO_ZfzX9i0qTS4Iub8R3Ru'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdTCbQZAAAAAHx_AZL_TND4HDGMPzdtn5_vNPTj'

app.config['SECRET_KEY'] = 'AkalasH'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:MY_parol@localhost:5432/posts'
db = SQLAlchemy(app)


UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
