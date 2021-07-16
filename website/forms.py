from flask_wtf import FlaskForm
from wtforms import  SelectField
from datetime import date
import pathlib
import json

from wtforms.fields.core import StringField
from wtforms.validators import InputRequired
  
# creating the date object of today's date
todays_date = date.today()

year_start = 2017
year_end = int(todays_date.year)
years = []
for i in reversed(range(year_start, year_end + 1)):
    years.append((i, i))


abb_dir = pathlib.Path(__file__).parents[1].absolute() / pathlib.Path("college_abbreviations.json")

with open(str(abb_dir), 'r') as file:
    abbreviations = json.load(file)

colleges = []
for college in abbreviations.keys():
    college_titled = college.title()
    colleges.append((college_titled, college_titled))


class CourseForm(FlaskForm):
    college = SelectField('College', choices=colleges)
    semester = SelectField('Semester', choices=[(
        'spring', 'Spring'), ('summer', 'Summer'), ('fall', 'Fall')])
    year = SelectField('Year', choices=years)
    professor = StringField('Professor', validators=[InputRequired("This field is required.")])