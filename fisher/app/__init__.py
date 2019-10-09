from flask import Flask
from app.secure import DEBUG
from app.models.base import db
from flask_login import LoginManager
from app.libs.email import mail

login_manager = LoginManager()


def register_blueprint(app):
    from app.web import web
    app.register_blueprint(web)


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.secure')
    app.config.from_object('app.setting')
    register_blueprint(app)
    db.init_app(app)
    db.create_all(app=app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "web.login"
    login_manager.login_message = '请先登录或注册！'

    with app.app_context():
        db.create_all()
    return app
