from flask_wtf import FlaskForm
from wtforms import  SelectField
from datetime import date
import pathlib

from wtforms.fields.core import StringField
from wtforms.validators import InputRequired

from ..parser_api.pdf_parser import get_colleges
  
# creating the date object of today's date
todays_date = date.today()

year_start = 2016
year_end = int(todays_date.year)
years = []
for i in reversed(range(year_start, year_end + 1)):
    years.append((i, i))

abbreviations = get_colleges()

colleges = []
for college in abbreviations.keys():
    college_titled = college.title()
    colleges.append((college, college_titled))


class CourseForm(FlaskForm):
    college = SelectField('College', choices=colleges)
    semester = SelectField('Semester', choices=[(
        'spring', 'Spring'), ('summer', 'Summer'), ('fall', 'Fall')])
    year = SelectField('Year', choices=years)
    professor = StringField('Professor', validators=[InputRequired("This field is required.")])