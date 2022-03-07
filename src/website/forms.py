from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField
from datetime import date

from wtforms.validators import InputRequired, NumberRange, Length, ValidationError

from ..parser_api.college_lookup import get_colleges

requiredStr = "This field is required."

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



class CollegeForm(FlaskForm):
    college = SelectField('College', choices=colleges, default='academic success center')
    semester = SelectField('Semester', choices=[(
        'spring', 'Spring'), ('summer', 'Summer'), ('fall', 'Fall')], default='spring')
    year = SelectField('Year', choices=years, default=str(year_end))


class ProfessorForm(FlaskForm):
    professor = StringField('Professor', validators=[InputRequired(requiredStr)])


class CourseForm(FlaskForm):
    course_abbr = StringField('Course Abbreviation', [InputRequired(requiredStr), Length(min=4, max=4,
        message="Course name must be a 4 letter abbreviation")])

    course_num = IntegerField('Course Number', validators=[InputRequired(requiredStr), NumberRange(min=100, max=999,
        message="Course number must be from 100 to 999")])
