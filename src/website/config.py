from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

FLASK_ENV = 'production'
TESTING = False
DEBUG = False
SECRET_KEY = environ.get('SECRET_KEY')
STATIC_FOLDER = './static'
TEMPLATES_FOLDER = './templates'

