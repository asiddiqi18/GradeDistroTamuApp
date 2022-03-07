import sqlalchemy.orm
from flask import Blueprint, render_template, request, g
from src.website.models import Grades, GradesMultiple
from src.website.forms import CourseForm
from src.website.views import render_default

bp = Blueprint('courses', __name__, url_prefix='/courses')


@bp.before_request
def get_url():
    g.url = request.url


@bp.route('/')
def courses_home():
    form = CourseForm()
    return render_template("course.html", form=form)


def get_courses(abbr, num):
    """ Retrieves list of grades from database if records exist or from PDF.
    Raises ValueError for invalid parameters """

    grades_query: sqlalchemy.orm.Query = Grades.query

    grades_query = grades_query.filter_by(department=abbr, course=num)

    grades = grades_query.all()

    return grades


@bp.route('/results', methods=["GET"])
def colleges():
    course_abbr = request.args.get('course_abbr').upper()
    course_num = request.args.get('course_num').lower()
    form = CourseForm(course_abbr=course_abbr, course_num=course_num)

    grades = get_courses(course_abbr, course_num)
    if not grades:
        return render_default('course.html', f'No results were found for {course_abbr} {course_num}', form)

    averages = GradesMultiple(grades)

    years_sorted, gpa_sorted = averages.sorted_years_and_gpa()
    courses_taught = ", ".join(averages.courses_taught)

    return render_template("course.html", grade_results=grades, form=form, averages=averages,
                           trend_year=years_sorted, trend_gpa=gpa_sorted)
