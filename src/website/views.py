from flask import Blueprint, render_template, request, flash
import requests

import plotly
import plotly.express as px

from .pdf_to_grades_parser import PdfParserDB
from .models import Grades, Professor
from . import db
from .forms import CourseForm
from . import unittest_db
views = Blueprint('views', __name__)


@views.route('/')
def home():
    form = CourseForm()
    source = "course"
    url = request.url
    print(url)
    return render_template("home.html", grade_results=None, form=form, source=source, url=url)


@views.route('/about', methods=["GET"])
def about():
    url = request.url
    return render_template("about.html", url=url)


@views.route('/professors', methods=["GET", "POST"])
def professor():

    def render_default(flash_message, form, source, url):
        flash(flash_message, 'error')
        return render_template("prof.html", grade_results=[], form=form, source=source, url=url, averages=None, trend_year=None, trend_gpa=None)

    source = "professor"
    url = request.url
    professor = request.args.get('professor')
    form = CourseForm(professor=professor)

    if len(professor) < 3:
        return render_default('This name is too short. Please enter a longer name.', form, source, url)

    elif len(professor) > 50:
        return render_default('This name is too long. Please enter a shorter name.', form, source, url)

    elif not all(x.isalpha() or x.isspace() for x in professor):
        return render_default('Professor names can only contain letters.', form, source, url)
    else:
        professors = Professor.query.filter(
            Professor.short_name.like(professor + "%")).first()
        if professors is None:
            return render_default('No results were found for this professor.', form, source, url)
        
    grades = professors.classes
    
    sum = 0
    averages = Grades()
    gpa_trend = {}

    for grade in grades:
        averages.merge(grade)
        sum += grade.gpa
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

    print(gpa_trend)

    averages.retrieve_percents()
    averages.gpa = sum / len(grades)
    averages.instructor = grades[0].instructor

    years = list(gpa_trend.keys())
    gpas = list(gpa_trend.values())

    zipped_lists = zip(years, gpas)

    sorted_pairs = sorted(zipped_lists)

    tuples = zip(*sorted_pairs)

    years_sorted, gpas_sorted = [ list(tuple) for tuple in  tuples]

    return render_template("prof.html", grade_results=grades, form=form, source=source, url=url, averages=averages, trend_year=years_sorted, trend_gpa=gpas_sorted)


@views.route('/test', methods=['GET'])
def test_unit():
    print("Starting unit tests...")
    unittest_db.unit_test()
    print("Finished unit tests!")
    return "Finished unit tests!"


@views.route('/test_single', methods=['GET'])
def test_single():
    print("Starting unit tests...")
    unittest_db.single_test("engineering", 2021, "spring")
    print("Finished unit tests!")
    return "Finished single test!"


@views.route('/results', methods=["GET", "POST"])
def result():
    source = "course"
    url = request.url
    college = request.args.get('college').lower()
    semester = request.args.get('semester').lower()
    year = request.args.get('year')
    form = CourseForm(college=college, semester=semester, year=year)

    print(f"{college}, {semester}, {year}")

    grades = Grades.query.filter_by(
        college=college, semester=semester, year=year).all()

    if (grades):
        print("Records in database... retrieving from database...")
    else:
        print("Records not in database... retrieving from PDF...")
        pdf_data = PdfParserDB(college, year, semester)

        try:
            results = pdf_data.text_extractor()
        except requests.exceptions.HTTPError:
            flash("There are no records for this semester.", category="error")
            return render_template("home.html", grade_results=[], form=form, source=source, url=url)

        grades = []
        for result in results:

            professor = Professor.query.filter_by(
                short_name=result[21]).first()
            if not professor:
                professor = Professor(short_name=result[21], full_name="null")
                db.session.add(professor)
                db.session.flush()
                db.session.commit()

            professor_id = professor.id

            new_grade = pdf_data.get_grade(result, professor_id)

            grades.append(new_grade)

        db.session.add_all(grades)
        db.session.commit()

    return render_template("home.html", grade_results=grades, form=form, source=source, url=url)


@views.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("not_found.html"), 404