from flask import Blueprint, render_template, request, g
from src.parser_api.college_lookup import get_colleges

bp = Blueprint('about', __name__, url_prefix='/about')

@bp.before_request
def get_url():
    g.url = request.url


@bp.route('/', methods=["GET"])
def about():
    return render_template("about.html")

