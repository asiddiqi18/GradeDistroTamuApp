from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from os import environ, path
from dotenv import load_dotenv
db = SQLAlchemy()
DB_NAME = "grades.db"


def create_app(debug=False):
    app = Flask(__name__, static_folder='./static', template_folder='./templates')

    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir, '.env'))

    app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    if not debug:
        from src.website.views import colleges, professors, courses, about, errors

        app.register_blueprint(colleges.bp)
        app.register_blueprint(professors.bp)
        app.register_blueprint(courses.bp)
        app.register_blueprint(about.bp)

        app.register_error_handler(404, errors.not_found)
        app.register_error_handler(400, errors.bad_request)
        app.register_error_handler(500, errors.server_error)

    create_database(app)

    return app


def create_database(app):
    if not path.exists('src/website/' + DB_NAME):
        print('Created database.')
        db.create_all(app=app)
