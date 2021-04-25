from flask import Flask
from flask_login import LoginManager
from flask_restful import Api


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdTCbQZAAAAAOSVAPFO_ZfzX9i0qTS4Iub8R3Ru'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdTCbQZAAAAAHx_AZL_TND4HDGMPzdtn5_vNPTj'

api = Api(app)
# app.register_blueprint(blueprint)
# app.register_blueprint(blueprint_users)

login_manager = LoginManager()
login_manager.init_app(app)

UPLOAD_FOLDER = 'app/static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

from app import routes
