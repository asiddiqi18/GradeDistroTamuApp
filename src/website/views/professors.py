from flask import Blueprint, render_template, request, flash, g
from src.website.models import Grades, Instructor, GradesMultiple
from src.website.forms import ProfessorForm
from src.website.views import render_default

bp = Blueprint('professors', __name__, url_prefix='/professors')


@bp.before_request
def get_url():
    g.url = request.url


@bp.route('/')
def professors_home():
    form = ProfessorForm()
    return render_template("professor.html", grade_results=[], form=form)


def handle_invalid_prof_params(prof):
    if len(prof) < 3:
        return 'This name is too short. Please enter a longer name.'
    if len(prof) > 50:
        return 'This name is too long. Please enter a shorter name.'
    if not all(x.isalpha() or x.isspace() or x == '-' for x in prof):
        return 'Professor names can only contain letters.'


@bp.route('/results', methods=["GET", "POST"])
def professors():
    professor_request = request.args.get('professor')
    form = ProfessorForm(professor=professor_request)

    error_msg = handle_invalid_prof_params(professor_request)

    if error_msg:
        return render_default('professor.html', error_msg, form)

    professors_query = Instructor.query.filter(
        Instructor.short_name.like(professor_request + "%")).first()
    if professors_query is None:
        return render_default('professor.html', 'No results were found for this professor.', form)

    grades = professors_query.classes

    averages = GradesMultiple(grades)

    years_sorted, gpa_sorted = averages.sorted_years_and_gpa()
    courses_taught = ", ".join(averages.courses_taught)

    return render_template("professor.html", grade_results=grades, form=form, averages=averages,
                           trend_year=years_sorted, trend_gpa=gpa_sorted, courses=courses_taught)
