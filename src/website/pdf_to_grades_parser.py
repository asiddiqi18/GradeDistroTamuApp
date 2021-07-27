from ..parser_api.pdf_parser import PdfParser, parent_dir
from .models import Grades
import pathlib

class PdfParserDB(PdfParser):

    def get_grade(self, result, professor_id):
            if not self.alt:
                return Grades(
                college=self.college,
                year=self.year,
                semester=self.semester,
                department=result[0],
                course=result[1],
                section=result[2],
                amount_A=result[3],
                percent_A=result[4],
                amount_B=result[5],
                percent_B=result[6],
                amount_C=result[7],
                percent_C=result[8],
                amount_D=result[9],
                percent_D=result[10],
                amount_F=result[11],
                percent_F=result[12],
                total_A_F=result[13],
                gpa=result[14],
                other_I=result[15],
                other_S=result[16],
                other_U=result[17],
                other_Q=result[18],
                other_X=result[19],
                other_total=result[20],
                instructor=result[21],
                professor_id=professor_id
            )
            else:
                return Grades(
                college=self.college,
                year=self.year,
                semester=self.semester,
                department=result[0],
                course=result[1],
                section=result[2],
                amount_A=result[6],
                percent_A=result[5],
                amount_B=result[7],
                percent_B=result[18],
                amount_C=result[8],
                percent_C=result[19],
                amount_D=result[9],
                percent_D=result[20],
                amount_F=result[10],
                percent_F=result[21],
                total_A_F=result[11],
                gpa=result[3],
                other_I=result[12],
                other_S=result[13],
                other_U=result[14],
                other_Q=result[15],
                other_X=result[16],
                other_total=result[17],
                instructor=result[4],
                professor_id=professor_id
            )

      
    @staticmethod
    def clean():
        dir_path = parent_dir / pathlib.Path("grades.db")
        if dir_path.exists():
            dir_path.unlink()
        # super().clean()