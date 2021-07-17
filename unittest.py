from datetime import date
from pdf_to_json import *
import logging
logging.basicConfig(filename="logs", filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

PdfToJson.clean()    

# get list of years from 2017 to current year
todays_date = date.today()
year_start = 2017
year_end = int(todays_date.year)
years = []
for i in reversed(range(year_start, year_end + 1)):
    years.append(i)


# get all college names from JSON file
abb_dir = pathlib.Path(__file__).parent.absolute() / pathlib.Path("college_abbreviations.json")
abbreviations = get_colleges()

# all school semesters
semesters = ["spring", "summer", "fall"]

errors = []
warnings = []

# unittest all data
for college in abbreviations.keys():
    for year in years:
        for semester in semesters:
            if year == 2021 and (semester == "summer" or semester == "fall"):
                continue
            test_info = f" [college={college}, year={year}, semester={semester}] "
            print(test_info.center(80, '='))
            pdf_json = PdfToJson(college, year, semester)
            try:
                json_file = pdf_json.save_json()
                if (json_file.stat().st_size < 100):
                    message = "Json size is less than 100 bytes (%s)" % test_info
                    warnings.append(message)
            except requests.exceptions.HTTPError:
                message = "HTTP error: Could not locate PDF for this entry. (%s)" % test_info
                errors.append(message)
                print(message)
            print("".center(80, '='))

print(" [Warnings] ".center(80, '#'))
for warning in warnings:
    print(warning)
print(" [Errors] ".center(80, '#'))
for error in errors:
    print(error)
