from flask import Blueprint, render_template, request, flash
from src.website.models import Grades, Instructor
from src.website.forms import CourseForm

bp = Blueprint('professors', __name__, url_prefix='/professors')


@bp.route('/')
def professors_home():
    form = CourseForm()
    url = request.url
    return render_template("professor.html", grade_results=[], form=form, url=url, averages=None, trend_year=None,
                           trend_gpa=None)


def handle_invalid_prof_params(prof):
    if len(prof) < 3:
        return 'This name is too short. Please enter a longer name.'
    if len(prof) > 50:
        return 'This name is too long. Please enter a shorter name.'
    if not all(x.isalpha() or x.isspace() or x == '-' for x in prof):
        return 'Professor names can only contain letters.'


@bp.route('/results', methods=["GET", "POST"])
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

    professors_query = Instructor.query.filter(
        Instructor.short_name.like(professor_request + "%")).first()
    if professors_query is None:
        return render_default('No results were found for this professor.', form, url)

    grades = professors_query.classes

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
