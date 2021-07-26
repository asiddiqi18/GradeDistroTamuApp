from datetime import date
from . import db
import requests
from .models import Grades, Professor

from ..parser_api.pdf_parser import get_colleges
from .pdf_to_grades_parser import PdfParserDB
import logging

# PdfParser.clean()

logging.basicConfig(filename="debug-report.log", filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger=logging.getLogger() 

def unit_test():


    # get list of years from 2017 to current year
    todays_date = date.today()
    year_start = 2017
    year_end = int(todays_date.year)
    years = []
    for i in reversed(range(year_start, year_end + 1)):
        years.append(i)


    # get all college names from JSON file
    abbreviations = get_colleges()

    # all school semesters
    semesters = ["spring", "summer", "fall"]

    # unittest all data
    for college in abbreviations.keys():
        for year in years:
            for semester in semesters:
                single_test(college, year, semester)


def single_test(college, year, semester):
    if year == 2021 and (semester == "summer" or semester == "fall"):
        return
    test_info = f" [college={college}, year={year}, semester={semester}] "
    logger.info(test_info.center(80, '='))
    pdf_json = PdfParserDB(college, year, semester, store_pdfs=True)
    try:
        results = pdf_json.text_extractor()

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

    except requests.exceptions.HTTPError:
        print("HTTP error: Could not locate PDF for this entry. (%s)" % test_info)
