from flask import Blueprint, render_template, request
from src.parser_api.college_lookup import get_colleges

bp = Blueprint('about', __name__, url_prefix='/about')


@bp.route('/', methods=["GET"])
def about():
    url = request.url
    return render_template("about.html", url=url)

