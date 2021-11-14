import json
from flask import Flask
from flask_mail import Mail
from flask_executor import Executor
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

login_manager = LoginManager()

mail = Mail()

executor = Executor()

def create_app() -> None:

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elar.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] =  "LeoEsJoto692316"

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = "elart.mexico@gmail.com"
    app.config['MAIL_PASSWORD'] = "Elart345"

    from .public import public_bp
    app.register_blueprint(public_bp)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .equipo import equipo_bp
    app.register_blueprint(equipo_bp)

    from .errors import errors_bp
    app.register_blueprint(errors_bp)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    executor.init_app(app)

    return app
    