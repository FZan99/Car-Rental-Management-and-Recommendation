from flask import Flask, request, json
import requests
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_recaptcha import ReCaptcha

db = SQLAlchemy()
DB_NAME = "carrental.db"


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    recaptcha = ReCaptcha(app=app)
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Car, Booking, Payment, Feedback

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.chooselogin'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    return app

def is_human(captcha_response):
    """ Validating recaptcha response from google server
        Returns True captcha test passed for submitted form else returns False.
    """
    secret = "6LfQaf8dAAAAAPJqxXrxguVwLc5MDW_mFmtjv7xA"
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
