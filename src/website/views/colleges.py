import sqlalchemy.orm
from flask import Blueprint, render_template, request, flash, g
import requests
from datetime import date
from src.parser_api.pdf_parser_model import PdfParserDB
from src.website.models import Grades
from src.website import db
from src.website.forms import CollegeForm
from src.parser_api.college_lookup import get_colleges
from src.website.views import render_default

bp = Blueprint('colleges', __name__)
colleges_json = get_colleges()
semesters = {'spring', 'summer', 'fall', 'all'}


@bp.before_request
def get_url():
    g.url = request.url


@bp.route('/')
@bp.route('/colleges')
def colleges_home():
    form = CollegeForm()
    return render_template("college.html", grade_results=None, form=form)


@bp.route('/colleges/results', methods=["GET", "POST"])
def colleges():
    college_request = request.args.get('college').lower()
    semester_request = request.args.get('semester').lower()
    year_request = request.args.get('year').lower()
    form = CollegeForm(college=college_request, semester=semester_request, year=year_request)

    try:
        grades = get_grades(college_request, year_request, semester_request)
    except ValueError as e:
        return render_default('college.html', str(e), form)

    return render_template("college.html", grade_results=grades, form=form)


def handle_invalid_college_params(college, semester, year) -> str:
    if year != 'all':
        if not year.isdigit():
            return "This is an invalid entry for year."
        year = int(year)
        if year < 2016:
            return "Records do not go this back."
        if year > date.today().year:
            return "This year is in the future."
    if semester not in semesters:
        return "This is not a valid semester."
    if college != 'all' and college not in colleges_json:
        return "This is not a valid college."


@bp.route('/api/v1/resources/grades', methods=['GET'])
def api_grades():
    required_params = ['college', 'semester', 'year']
    for req in required_params:
        if req not in request.args:
            return f"Expected {req} parameter"

    college_request = request.args.get('college').lower()
    semester_request = request.args.get('semester').lower()
    year_request = request.args.get('year').lower()

    try:
        grades = get_grades(college_request, year_request, semester_request)
    except ValueError as e:
        return str(e)

    pdf_data = PdfParserDB(college_request, int(year_request), semester_request)
    grades_dict = pdf_data.get_dictionary(grades)
    return grades_dict


def get_grades(college, year, semester):
    """ Retrieves list of grades from database if records exist or from PDF.
    Raises ValueError for invalid parameters """
    error_msg = handle_invalid_college_params(college, semester, year)

    if error_msg:
        raise ValueError(error_msg)

    grades_query: sqlalchemy.orm.Query = Grades.query

    grades_query = grades_query.filter_by(college=college, semester=semester, year=year)

    grades = grades_query.all()

    if not grades:  # no records exist
        try:
            pdf_data = PdfParserDB(college, int(year), semester)
            grades = pdf_data.get_grades_obj()
        except (ValueError, requests.exceptions.HTTPError):
            raise ValueError("There are no records for this semester.")

        db.session.add_all(grades)
        db.session.commit()

    return grades

