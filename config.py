
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# load flask app
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base config."""
    
    # folders and forms secret key
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # upload files default config
    UPLOAD_PATH = os.path.join(basedir, 'application/temp')
    ALLOWED_EXTENSIONS = ['xlsx']
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # mail logging config
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = os.environ.get('ADMINS')

    ROWS_PER_PAGE = 10

class ProdConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False

    # sqlalchemy config vars
    # prod database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
    ENV = 'development'
    DEBUG = True
    TESTING = True

    # sqlalchemy config vars
    # development database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
