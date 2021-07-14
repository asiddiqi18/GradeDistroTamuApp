from flask import Blueprint, render_template, request, flash
from pdf_to_json import *
from .models import Grades
from . import db
views = Blueprint('views', __name__)

# https://www.youtube.com/watch?v=dam0GPOAvVI

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/results', methods=["GET", "POST"])
def result():
    college = request.args['college']
    semester = request.args['semester']
    year = request.args['year']
    print(f"{college}, {semester}, {year}")

    pdf_json = PdfToJson(college, year, semester)
    results = pdf_json.get_list_of_lists()

    for result in results:
            department = result[0]
            course = result[1]
            section = result[2]

            amount_A = result[3]
            amount_B = result[5]
            amount_C = result[7]
            amount_D = result[9]
            amount_F = result[11]

            percent_A = result[4]
            percent_B = result[6]
            percent_C = result[8]
            percent_D = result[10]
            percent_F = result[12]

            total_A_F = result[13]
            gpa = result[14]

            other_I = result[15]
            other_S = result[16]
            other_U = result[17]
            other_Q = result[18]
            other_X = result[19]
            other_total = result[20]

            instructor = result[21]

            new_grade = Grades(
                department = department, 
                course = course,
                section = section,
                amount_A = amount_A,
                percent_A =  percent_A,
                amount_B =  amount_B,
                percent_B =  percent_B,
                amount_C =  amount_C,
                percent_C =  percent_C,
                amount_D =  amount_D,
                percent_D =  percent_D,
                amount_F =  amount_F,
                percent_F =  percent_F,
                total_A_F =  total_A_F,
                gpa =  gpa,
                other_I =  other_I,
                other_S =  other_S,
                other_U =  other_U,
                other_Q =  other_Q,
                other_X =  other_X,
                other_total =  other_total,
                instructor =  instructor
            )

            db.session.add(new_grade)
            db.session.commit()

    print(results)

    return render_template("home.html")