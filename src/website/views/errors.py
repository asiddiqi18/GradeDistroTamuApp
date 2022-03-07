from flask import Blueprint, render_template, make_response

bp = Blueprint('error', __name__, url_prefix='/error')


@bp.errorhandler(404)
def not_found(e):
    """ Page not found """
    return make_response(
        render_template("errors.html", msg="Page not found"),
        404
    )


@bp.errorhandler(400)
def bad_request(e):
    """ Bad request """
    return make_response(
        render_template("errors.html", msg="Bad request"),
        400
    )


@bp.errorhandler(500)
def server_error(e):
    """ Internal server error """
    return make_response(
        render_template("errors.html", msg="Internal server error"),
        500
    )