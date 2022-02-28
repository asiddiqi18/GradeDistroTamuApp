import logging

from .pdf_parser import PdfParser
from ..website.models import Grades, Professor
from ..website import db


class PdfParserDB(PdfParser):

    def __init__(self, college: str, year: int, semester: str):
        super().__init__(college, year, semester, True)

    def get_grades_obj(self):
        """ Serializes the PDF results to Python dictionary object """
        list_of_courses = self.text_extractor()
        if len(list_of_courses) == 0:
            logging.warning("No courses were found.")
            return None

        results = []

        for result in list_of_courses:

            if len(result) != self.arg_expect_amount:
                raise RuntimeError("Incorrect number of attributes in course info. Got %d, expected %d.", len(result),
                                   self.arg_expect_amount)

            grade = Grades()

            grade.college = self.college
            grade.year = self.year
            grade.semester = self.semester

            grade.department = result[0]
            grade.course = result[1]
            grade.section = result[2]

            if not self.alt:
                grade.amount_A = result[3]
                grade.amount_B = result[5]
                grade.amount_C = result[7]
                grade.amount_D = result[9]
                grade.amount_F = result[11]
                grade.percent_A = result[4]
                grade.percent_B = result[6]
                grade.percent_C = result[8]
                grade.percent_D = result[10]
                grade.percent_F = result[12]
                grade.total_A_F = result[13]
                grade.gpa = result[14]
                grade.other_I = result[15]
                grade.other_S = result[16]
                grade.other_U = result[17]
                grade.other_Q = result[18]
                grade.other_X = result[19]
                grade.other_total = result[20]
                grade.instructor = result[21]
            else:
                grade.amount_A = result[6]
                grade.amount_B = result[7]
                grade.amount_C = result[8]
                grade.amount_D = result[9]
                grade.amount_F = result[10]
                grade.percentage_A = result[5]
                grade.percentage_B = result[18]
                grade.percentage_C = result[19]
                grade.percentage_D = result[20]
                grade.percentage_F = result[21]
                grade.total_A_F = result[11]
                grade.gpa = result[3]
                grade.other_I = result[12]
                grade.other_S = result[13]
                grade.other_U = result[14]
                grade.other_Q = result[15]
                grade.other_X = result[16]
                grade.other_total = result[17]
                grade.instructor = result[4]

            prof = Professor.query.filter_by(
                short_name=grade.instructor).first()
            if not prof:
                prof = Professor(short_name=grade.instructor, full_name="null")
                db.session.add(prof)
                db.session.flush()
                db.session.commit()

            grade.professor_id = prof.id

            results.append(grade)

        return results
