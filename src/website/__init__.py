from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "grades.db"


def create_app(debug=False):
    app = Flask(__name__, static_folder='./static', template_folder='./templates')
    app.config['SECRET_KEY'] = 'this is a secret key :)'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    if not debug:
        from src.website.views import colleges, professors, about

        app.register_blueprint(colleges.bp)
        app.register_blueprint(professors.bp)
        app.register_blueprint(about.bp)
        # app.register_error_handler(404, page_not_found)

    create_database(app)

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created database.')
