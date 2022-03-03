import logging

from .pdf_parser import PdfParser
from ..website.models import Grades, Instructor
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

            grade = Grades()

            grade.college = self.college
            grade.year = self.year
            grade.semester = self.semester

            grade.department = result['department']
            grade.course = result['course']
            grade.section = result['section']

            grade.amount_a = result['amount_a']
            grade.amount_b = result['amount_b']
            grade.amount_c = result['amount_c']
            grade.amount_d = result['amount_d']
            grade.amount_f = result['amount_f']
            grade.percent_a = result['percent_a']
            grade.percent_b = result['percent_b']
            grade.percent_c = result['percent_c']
            grade.percent_d = result['percent_d']
            grade.percent_f = result['percent_f']
            grade.total = result['total']
            grade.gpa = result['gpa']
            grade.other_i = result['other_i']
            grade.other_s = result['other_s']
            grade.other_u = result['other_u']
            grade.other_q = result['other_q']
            grade.other_x = result['other_x']
            grade.other_total = result['other_total']
            grade.professor = result['professor']

            prof = Instructor.query.filter_by(
                short_name=grade.professor).first()
            if not prof:
                prof = Instructor(short_name=grade.professor, full_name="null")
                logging.info(f"Found new professor {grade.professor}...")
                db.session.add(prof)
                db.session.flush()
                db.session.commit()
                logging.info("Added new professor")

            grade.instructor_id = prof.id

            results.append(grade)

        return results

    def get_dictionary(self, lst_of_grades=None):
        lst_of_grades_dict = []
        for g in lst_of_grades:
            lst_of_grades_dict.append(
                {k: str(v) for k, v in g.__dict__.items() if not (k.startswith('__') and k.endswith('__'))}
            )
            dct = {
                'college': self.college,
                'year': self.year,
                'semester': self.semester
            }
            for k, v in g.__dict__.items():
                if not (k.startswith('__') and k.endswith('__')):
                    dct[k] = str(v)
            lst_of_grades_dict.append(dct)

        return super(PdfParserDB, self).get_dictionary(lst_of_grades_dict)
