import os

from flask import Flask, current_app
from flask_login import LoginManager
from config import DevConfig, ProdConfig

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# python default logging package
# logs in console, file and mail
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask_bootstrap import Bootstrap

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please login to continue"
db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()

def create_app(config_class=DevConfig):

    app = Flask(__name__)
    # import dev config
    app.config.from_object(config_class)

    bootstrap.init_app(app)

    with app.app_context():

        login_manager.init_app(app)

        db.init_app(app)
        migrate.init_app(app, db)
        
        configure_logging(app)

        from application import routes, errors

        from application.auth import bp as auth_bp
        app.register_blueprint(auth_bp)

        from application.main import bp as main_bp
        app.register_blueprint(main_bp)

        from application.auth.models import User
        from application.main.models import Balance, Credit

        @app.shell_context_processor
        def make_shell_context():
            return {'db': db, 'User': User, 'Balance': Balance, 'Credit': Credit}

        @login_manager.user_loader
        def load_user(id):
            return User.query.get(int(id))

        return app


def configure_logging(app):

    # handler type -> console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(verbose_formatter())

    # handler type -> file
    app_dir = os.path.abspath(os.path.dirname(__file__))
    log_dir = os.path.join(app_dir, '../logs/')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    file_handler = RotatingFileHandler(os.path.join(log_dir, 'app_logs.log'), 
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(verbose_formatter())

    # set level of event message and 
    # add handler by type of flask env
    if app.debug:
        # show all the info
        app.logger.setLevel(logging.DEBUG)

        console_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(console_handler)
        app.logger.addHandler(file_handler)
    else:
        # show only error messages
        app.logger.setLevel(logging.ERROR)

        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
        app.logger.addHandler(file_handler)

        # add handler type -> mail
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'],
                subject='Microblog Failure',
                credentials=auth,
                secure=secure
                )
            mail_handler.setFormatter(mail_handler_formatter())
            mail_handler.setLevel(logging.DEBUG)
            app.logger.addHandler(mail_handler)

def verbose_formatter():
    return logging.Formatter(
        '[%(asctime)s.%(msecs)d]\t %(levelname)s \t[%(name)s.%(funcName)s:%(lineno)d]\t %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )

def mail_handler_formatter():
    return logging.Formatter(
        '''
            Message type:       %(levelname)s
            Location:           %(pathname)s:%(lineno)d
            Module:             %(module)s
            Function:           %(funcName)s
            Time:               %(asctime)s.%(msecs)d
            Message:
            %(message)s
        ''',
        datefmt='%d/%m/%Y %H:%M:%S'
    )