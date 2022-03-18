from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "grades.db"


def create_app(unit_testing=False):
    app = Flask(__name__)

    app.config.from_object('src.website.config.ProdConfig')
    db.init_app(app)

    if not unit_testing:
        from src.website.views import colleges, professors, courses, errors

        app.register_blueprint(colleges.bp)
        app.register_blueprint(professors.bp)
        app.register_blueprint(courses.bp)

        app.register_error_handler(404, errors.not_found)
        app.register_error_handler(400, errors.bad_request)
        app.register_error_handler(500, errors.server_error)

    create_database(app)

    return app


def create_database(app):
    if not path.exists('src/website/' + DB_NAME):
        print('Created database.')
        db.create_all(app=app)
