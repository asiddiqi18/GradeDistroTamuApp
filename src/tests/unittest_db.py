from datetime import date
from src.website import create_app, db
import requests

from src.parser_api.pdf_parser import get_colleges
from src.parser_api.pdf_parser_model import PdfParserDB, PdfParser
import logging
import sys
import os

# PdfParser.clean()

app = create_app(True)
print("Running unit tests")
app.app_context().push()

logging.basicConfig(filename="debug-report.log", filemode='a', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f'{os.path.basename(__file__)}.log'),
                        logging.StreamHandler(sys.stdout),
                    ])
logger = logging.getLogger()

warnings = []
errors = []


class NoCourses(Exception):
    pass


def single_test_db(college, year, semester):
    test_info = f" [college={college}, year={year}, semester={semester}] "
    logger.info(test_info.center(80, '='))
    pdf_json = PdfParserDB(college, year, semester)
    try:
        logging.info("Converting to Grades object...")
        grades = pdf_json.get_grades_obj()
        logging.info("Converted successfully!")
        if not grades:
            raise NoCourses
        logging.info("Adding to database...")
        db.session.add_all(grades)
        db.session.commit()
        logging.info("Successfully added to database!")

    except requests.exceptions.HTTPError:
        errors.append(f"HTTP error: Could not locate PDF for this entry. ({test_info})")
    except NoCourses:
        errors.append(f"No Courses: Could not find any courses. ({test_info})")


def single_test_json(college, year, semester):
    test_info = f" [college={college}, year={year}, semester={semester}] "
    logger.info(test_info.center(80, '='))
    parser = PdfParser(college, year, semester, store_pdfs=True)
    try:
        json_file = parser.save_json()
        if json_file.stat().st_size < 100:
            message = "Json size is less than 100 bytes (%s)" % test_info
            warnings.append(message)
    except requests.exceptions.HTTPError:
        message = "HTTP error: Could not locate PDF for this entry. (%s)" % test_info
        errors.append(message)
    logger.info("".center(80, '='))


def unit_test(test):
    # get list of years from 2017 to current year
    today_date = date.today()
    year_start = 2017
    year_end = int(today_date.year)
    month_end = int(today_date.month)
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

                # don't perform test on current year given a semester if semester isn't over yet
                if year == year_end:
                    if semester == "spring" and month_end <= 5:
                        continue
                    elif semester == "summer" and month_end <= 8:
                        continue
                    elif semester == "fall":
                        continue

                test(college, year, semester)

    print(" [Errors] ".center(80, '#'))
    for error in errors:
        logger.error(error)


if __name__ == '__main__':
    unit_test(single_test_db)
