from flask import Blueprint, render_template, request, flash
from pdf_to_json import *
from .models import Grades
from . import db
views = Blueprint('views', __name__)

# https://www.youtube.com/watch?v=dam0GPOAvVI


@views.route('/')
def home():
    return render_template("home.html", grade_results=[])


@views.route('/results', methods=["GET", "POST"])
def result():
    college = request.args['college']
    semester = request.args['semester']
    year = request.args['year']
    print(f"{college}, {semester}, {year}")

    grades = Grades.query.filter_by(
        college=college, semester=semester, year=year).all()

    if (grades):
        print("Records in database... retrieving from database...")
    else:
        print("Records not in database... retrieving from PDF...")
        pdf_json = PdfToJson(college, year, semester)
        results = pdf_json.get_list_of_lists()
        grades = []
        for result in results:
            new_grade = Grades(
                college=college,
                year=year,
                semester=semester,
                department=result[0],
                course=result[1],
                section=result[2],
                amount_A=result[3],
                percent_A=result[4],
                amount_B=result[5],
                percent_B=result[6],
                amount_C=result[7],
                percent_C=result[8],
                amount_D=result[9],
                percent_D=result[10],
                amount_F=result[11],
                percent_F=result[12],
                total_A_F=result[13],
                gpa=result[14],
                other_I=result[15],
                other_S=result[16],
                other_U=result[17],
                other_Q=result[18],
                other_X=result[19],
                other_total=result[20],
                instructor=result[21]
            )

            grades.append(new_grade)

        db.session.add_all(grades)
        db.session.commit()

    with open('website/tmp/debug_grades.txt', 'w') as file:
        for grade in grades:
            file.write(grade.__repr__() + '\n')

    return render_template("home.html", grade_results=grades)
