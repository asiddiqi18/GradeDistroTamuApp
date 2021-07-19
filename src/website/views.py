from flask import Blueprint, render_template, request, flash
import requests
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
    source = "professor"
    url = request.url
    professor = request.args.get('professor')
    form = CourseForm(professor=professor)
    professors = Professor.query.filter(Professor.short_name.like(professor + "%")).first()
    print(professors.__repr__())
    if professors is None:
        flash('No results were found for this professor.', category='error')
        grades = []
    else:
        grades = professors.classes
    return render_template("home.html", grade_results=grades, form=form, source=source, url=url)


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

    grades = Grades.query.filter_by(college=college, semester=semester, year=year).all()

    if (grades):
        print("Records in database... retrieving from database...")
    else:
        print("Records not in database... retrieving from PDF...")
        pdf_json = PdfParserDB(college, year, semester)

        try:
            results = pdf_json.text_extractor()
        except requests.exceptions.HTTPError:
            flash("There are no records for this semester.", category="error")
            return render_template("home.html", grade_results=[], form=form, source=source, url=url)

        grades = []
        for result in results:

            professor = Professor.query.filter_by(short_name=result[21]).first()
            if not professor:
                professor = Professor(short_name=result[21], full_name="null")
                db.session.add(professor)
                db.session.flush()
                db.session.commit()

            professor_id = professor.id
                
            new_grade = pdf_json.get_grade(result, professor_id)

            grades.append(new_grade)

        db.session.add_all(grades)
        db.session.commit()

    return render_template("home.html", grade_results=grades, form=form, source=source, url=url)

    
@views.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("not_found.html")
