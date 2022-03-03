from flask_wtf import FlaskForm
from wtforms import SelectField
from datetime import date

from wtforms.fields.core import StringField
from wtforms.validators import InputRequired

from ..parser_api.college_lookup import get_colleges

# creating the date object of today's date
today_date = date.today()

year_start = 2016
year_end = int(today_date.year)
years = []
for i in reversed(range(year_start, year_end + 1)):
    years.append((i, i))

abbreviations = get_colleges()

colleges = []
for college in abbreviations.keys():
    college_titled = college.title()
    colleges.append((college, college_titled))


class CourseForm(FlaskForm):
    college = SelectField('College', choices=colleges, default='academic success center')
    semester = SelectField('Semester', choices=[(
        'spring', 'Spring'), ('summer', 'Summer'), ('fall', 'Fall')], default='spring')
    year = SelectField('Year', choices=years, default=str(year_end))
    professor = StringField('Professor', validators=[InputRequired("This field is required.")])
