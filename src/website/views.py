import sqlalchemy.orm
from flask import Blueprint, render_template, request, flash, jsonify
import requests
from datetime import date
from ..parser_api.pdf_parser_model import PdfParserDB
from .models import Grades, Instructor
from . import db
from .forms import CourseForm
from ..parser_api.college_lookup import get_colleges

views = Blueprint('views', __name__)
colleges_json = get_colleges()
semesters = {'spring', 'summer', 'fall', 'all'}


@views.route('/')
@views.route('/colleges')
def colleges_home():
    form = CourseForm()
    url = request.url
    print(url)
    return render_template("college.html", grade_results=None, form=form, url=url)


@views.route('/professors')
def professors_home():
    form = CourseForm()
    url = request.url
    return render_template("professor.html", grade_results=[], form=form, url=url, averages=None, trend_year=None,
                           trend_gpa=None)


@views.route('/about', methods=["GET"])
def about():
    url = request.url
    return render_template("about.html", url=url)


def handle_invalid_prof_params(prof):
    if len(prof) < 3:
        return 'This name is too short. Please enter a longer name.'
    if len(prof) > 50:
        return 'This name is too long. Please enter a shorter name.'
    if not all(x.isalpha() or x.isspace() or x == '-' for x in prof):
        return 'Professor names can only contain letters.'


@views.route('/professors/results', methods=["GET", "POST"])
def professors():
    def render_default(flash_message, _form, _url):
        flash(flash_message, 'error')
        return render_template("professor.html", grade_results=[], form=_form, url=_url, averages=None, trend_year=None,
                               trend_gpa=None)

    url = request.url
    professor_request = request.args.get('professor')
    form = CourseForm(professor=professor_request)

    error_msg = handle_invalid_prof_params(professor_request)

    if error_msg:
        return render_default(error_msg, form, url)

    professors = Instructor.query.filter(
        Instructor.short_name.like(professor_request + "%")).first()
    if professors is None:
        return render_default('No results were found for this professor.', form, url)

    grades = professors.classes

    sum_gpa = 0
    averages = Grades()
    gpa_trend = {}
    courses_taught = set()

    for grade in grades:
        averages.merge(grade)
        sum_gpa += grade.gpa
        courses_taught.add(f"{grade.department} {grade.course}")
        if grade.year not in gpa_trend:
            total = grade.gpa
            length = 1
        else:
            total, length = gpa_trend[grade.year]
            total += grade.gpa
            length += 1
        gpa_trend[grade.year] = (total, length)

    for key in gpa_trend.keys():
        total, length = gpa_trend[key]
        gpa_trend[key] = float(total / length)

    courses_taught = ", ".join(sorted(courses_taught))

    averages.retrieve_percents()
    averages.gpa = sum_gpa / len(grades)
    averages.professor = grades[0].professor

    years = list(gpa_trend.keys())
    gpa_list = list(gpa_trend.values())

    zipped_lists = zip(years, gpa_list)
    sorted_pairs = sorted(zipped_lists)
    tuples = zip(*sorted_pairs)
    years_sorted, gpa_sorted = [list(tup) for tup in tuples]

    return render_template("professor.html", grade_results=grades, form=form, url=url, averages=averages,
                           trend_year=years_sorted, trend_gpa=gpa_sorted, courses=courses_taught)


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


@views.route('/colleges/results', methods=["GET", "POST"])
def colleges():
    def render_default(flash_message, _form, _url):
        flash(flash_message, 'error')
        return render_template("college.html", grade_results=[], form=form, url=url)

    url = request.url
    college_request = request.args.get('college').lower()
    semester_request = request.args.get('semester').lower()
    year_request = request.args.get('year').lower()
    form = CourseForm(college=college_request, semester=semester_request, year=year_request)

    try:
        grades = get_grades(college_request, year_request, semester_request)
    except ValueError as e:
        return render_default(str(e), form, url)

    return render_template("college.html", grade_results=grades, form=form, url=url)


@views.route('/api/v1/resources/grades', methods=['GET'])
def api_grades():
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


@views.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("not_found.html")
