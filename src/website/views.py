from flask import Blueprint, render_template, request, flash
import requests

from ..parser_api.pdf_parser_model import PdfParserDB
from .models import Grades, Professor
from . import db
from .forms import CourseForm



views = Blueprint('views', __name__)


@views.route('/')
def home():
    form = CourseForm()
    url = request.url
    print(url)
    return render_template("home.html", grade_results=None, form=form, url=url)


@views.route('/about', methods=["GET"])
def about():
    url = request.url
    return render_template("about.html", url=url)


@views.route('/professors', methods=["GET", "POST"])
def professor():
    def render_default(flash_message, _form, _url):
        flash(flash_message, 'error')
        return render_template("prof.html", grade_results=[], form=_form, url=_url, averages=None, trend_year=None,
                               trend_gpa=None)

    url = request.url
    professor_request = request.args.get('professor')
    form = CourseForm(professor=professor_request)

    if len(professor_request) < 3:
        return render_default('This name is too short. Please enter a longer name.', form, url)
    elif len(professor_request) > 50:
        return render_default('This name is too long. Please enter a shorter name.', form, url)
    elif not all(x.isalpha() or x.isspace() or x == '-' for x in professor_request):
        return render_default('Professor names can only contain letters.', form, url)
    else:
        professors = Professor.query.filter(
            Professor.short_name.like(professor_request + "%")).first()
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
    averages.instructor = grades[0].instructor

    years = list(gpa_trend.keys())
    gpa_list = list(gpa_trend.values())

    zipped_lists = zip(years, gpa_list)

    sorted_pairs = sorted(zipped_lists)

    tuples = zip(*sorted_pairs)

    years_sorted, gpa_sorted = [list(tup) for tup in tuples]

    return render_template("prof.html", grade_results=grades, form=form, url=url, averages=averages,
                           trend_year=years_sorted, trend_gpa=gpa_sorted, courses=courses_taught)


@views.route('/results', methods=["GET", "POST"])
def result():
    url = request.url
    college = request.args.get('college').lower()
    semester = request.args.get('semester').lower()
    year = request.args.get('year').lower()
    form = CourseForm(college=college, semester=semester, year=year)

    grades = Grades.query.filter_by(
        college=college, semester=semester, year=year).all()

    if not grades:  # no records exist
        try:
            pdf_data = PdfParserDB(college, int(year), semester)
            grades = pdf_data.get_grades_obj()
        except requests.exceptions.HTTPError:
            flash("There are no records for this semester.", category="error")
            return render_template("home.html", grade_results=[], form=form, url=url)
        except ValueError:
            flash(f"Please enter a valid year.", category="error")
            return render_template("home.html", grade_results=[], form=form, url=url)

        db.session.add_all(grades)
        db.session.commit()

    return render_template("home.html", grade_results=grades, form=form, url=url)


@views.errorhandler(404)
def page_not_found():
    # note that we set the 404 status explicitly
    return render_template("not_found.html"), 404
