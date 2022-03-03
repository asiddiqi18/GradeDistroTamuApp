import requests
import pathlib
import re
import PyPDF2
import json
import logging
import shutil
from .college_lookup import get_colleges

# Get the directory this file is in, as pathlib object.
parent_dir = pathlib.Path(__file__).parent.absolute()


class PdfParser:
    """ API to parse PDFs from the grade distribution registrar """

    # Setup logging for debugging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    # Currently disabled
    # logging.disable(logging.INFO)

    # Regex to extract info from PDF binaries.
    # regex_main is used for most retrievals
    regex_main = re.compile(
        r'(?P<department>\D{4})-(?P<course>\d{3,4})-(?P<section>\d{3})\s+(?P<amount_a>\d+)\s+('
        r'?P<percent_a>\d+.\d+)%\s+(?P<amount_b>\d+)\s+(?P<percent_b>\d+.\d+)%\s+('
        r'?P<amount_c>\d+)\s+(?P<percent_c>\d+.\d+)%\s+(?P<amount_d>\d+)\s+('
        r'?P<percent_d>\d+.\d+)%\s+(?P<amount_f>\d+)\s+(?P<percent_f>\d+.\d+)%\s+('
        r'?P<total>\d+)\s+(?P<gpa>\d+.\d+)\s+(?P<other_i>\d+)\s+(?P<other_s>\d+)\s+(?P<other_u>\d+)\s+('
        r'?P<other_q>\d+)\s+(?P<other_x>\d+)\s+(?P<other_total>\d+)\s+(?P<professor>'
        r'\S+\s\w)')

    # However, most PDFs from 2016 are formatted slightly different, requiring an alternative pattern
    regex_alt = re.compile(
        r'(?P<department>\D{4})-(?P<course>\d{3,4})-(?P<section>\d{3})\s+(?P<gpa>\d+.\d+)\s+(?P<professor>\S+\s\w)\s('
        r'?P<percent_a>\d+.\d+)%\s+(?P<amount_a>\d+)\s+(?P<amount_b>\d+)\s+('
        r'?P<amount_c>\d+)\s+(?P<amount_d>\d+)\s+(?P<amount_f>\d+)\s+(?P<total>\d+)\s+('
        r'?P<other_i>\d+)\s+(?P<other_s>\d+)\s+(?P<other_u>\d+)\s+(?P<other_q>\d+)\s+(?P<other_x>\d+)\s+('
        r'?P<other_total>\d+)\s+(?P<percent_b>\d+.\d+)%\s+(?P<percent_c>\d+.\d+)%\s+('
        r'?P<percent_d>\d+.\d+)%\s+(?P<percent_f>\d+.\d+)%')

    def __init__(self, college: str, year: int, semester: str, store_pdfs=False):
        self.college = college
        self.year = year
        self.semester = semester
        self.arg_expect_amount = 22
        self.semesters = {"spring": 1, "summer": 2, "fall": 3}
        self.json = None
        self.alt = False
        self.pdf_path = None
        self.store_pdfs = store_pdfs

        # Validate parameters
        abbreviation_dict = get_colleges()
        if self.college.lower() not in abbreviation_dict:
            raise ValueError(
                f"College '{self.college}' not identified. Enter one of these following colleges: \
                {', '.join(list(abbreviation_dict.keys()))}")
        if int(self.year) < 2016:
            raise ValueError("Data for years before 2016 do not exist!")
        if self.semester not in self.semesters:
            raise ValueError(
                f"Semester '{self.semester}' not identified")

    def file_name(self):
        """ Generate a safe file name for the PDF from the parameters """
        filename = "%s_%s_%s" % (self.college, self.year, self.semester)
        dangerous_chars = [' ', '/']
        for danger in dangerous_chars:
            filename = filename.replace(danger, "_")
        return filename

    def get_pdf_path(self):
        # Get/create directory for PDFs, and get path of the pdf that will be downloaded/is saved
        file_name = self.file_name() + ".pdf"
        pdf_dir = parent_dir / pathlib.Path("pdf")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        return pdf_dir / pathlib.Path(file_name)

    def semester_to_numeric_code(self):
        """ Get the numerical coding used for the URL from the semester """
        return self.semesters[self.semester]

    def get_college_abbreviation(self):
        abbreviation_dict = get_colleges()
        return abbreviation_dict[self.college.lower()]

    def download_pdf(self):
        """
            Downloads grade reports to current directory from web
            Saves PDF to '../pdf'
            Returns path of downloaded PDF / existing PDF
        """

        pdf_path = self.get_pdf_path()

        # If PDF not already downloaded, then request it from URL
        if not pdf_path.exists():
            logging.info("PDF does not exist, downloading PDF...")
            # Generate a URL by converting parameters to values expected by URL
            abbreviation = self.get_college_abbreviation()
            year_semester = str(self.year) + str(self.semester_to_numeric_code())

            url = 'https://web-as.tamu.edu/GradeReports/PDFReports/%s/grd%s%s.pdf' % (
                year_semester, year_semester, abbreviation)

            res = requests.get(url)
            res.raise_for_status()

            # write as binary
            with open(pdf_path, 'wb') as f:
                f.write(res.content)

            logging.info("PDF downloaded!")

    def text_extractor(self) -> list:
        """
            Parses the grade distribution PDF for its information using regex pattern.
            Returns a list of dictionaries, each dictionary containing info about a particular course section
        """

        # If this function is called without downloading the PDF first, then download the PDF
        self.download_pdf()

        logging.info("Extracting PDF...")

        # Otherwise, use regex pattern to extract information
        # Regex patterns precompiled above.
        with open(self.get_pdf_path(), 'rb') as f:
            pdf = PyPDF2.PdfFileReader(f)
            number_of_pages = pdf.getNumPages()

            results = []

            for p in range(number_of_pages):
                page = pdf.getPage(p)
                text = page.extractText()
                regex_result = [m.groupdict() for m in self.regex_main.finditer(text)]
                # If this regex pattern did not yield anything, then try using the alternative regex pattern
                if len(regex_result) == 0:
                    regex_result = [m.groupdict() for m in self.regex_alt.finditer(text)]
                    if len(regex_result) != 0:
                        self.alt = True  # Designate that alternative pattern was used for future uses

                # Append all results to a master list
                results.extend(regex_result)

        # Depending on setting put in constructor, delete PDF from computer after extracting its text
        if not self.store_pdfs:
            pathlib.Path.unlink(self.pdf_path)

        logging.info("Finished extracting!")
        return results

    def get_dictionary(self, lst_of_grades_dict=None):
        """ Serializes the PDF results to Python dictionary object """

        if not lst_of_grades_dict:
            lst_of_grades_dict: list = self.text_extractor()
            if len(lst_of_grades_dict) == 0:
                logging.warning("No courses were found.")
                return None

        results_dict = {}

        for result in lst_of_grades_dict:
            department = result['department']
            course = result['course']
            section = result['section']

            amount = {}
            percentage = {}
            other = {}

            amount['A'] = result['amount_a']
            amount['B'] = result['amount_b']
            amount['C'] = result['amount_c']
            amount['D'] = result['amount_d']
            amount['F'] = result['amount_f']

            percentage['A'] = result['percent_a']
            percentage['B'] = result['percent_b']
            percentage['C'] = result['percent_c']
            percentage['D'] = result['percent_d']
            percentage['F'] = result['percent_f']

            total = result['total']
            gpa = result['gpa']

            other['I'] = result['other_i']
            other['S'] = result['other_s']
            other['U'] = result['other_u']
            other['Q'] = result['other_q']
            other['X'] = result['other_x']
            other['total'] = result['other_total']

            professor = result['professor']

            section_dict = {
                "amount": amount,
                "percentage": percentage,
                "total": total,
                "gpa": gpa,
                "other": other,
                "professor": professor
            }

            college = result.get('college', self.college)
            year = result.get('year', self.year)
            semester = result.get('semester', self.semester)

            results_dict.setdefault(college, {})
            results_dict[college].setdefault(year, {})
            results_dict[college][year].setdefault(semester, {})
            results_dict[college][year][semester].setdefault(department, {})
            results_dict[college][year][semester][department].setdefault(course, {})
            results_dict[college][year][semester][department][course][section] = section_dict

        return results_dict

    @staticmethod
    def clean():
        """ Static method to delete all local files related to this API. Useful for testing. """
        dir_names = ["json", "pdf"]
        for d in dir_names:
            dir_path = parent_dir / pathlib.Path(d)
            if dir_path.is_dir():
                folder = str(dir_path)
                shutil.rmtree(folder)
                logging.info("Successfully deleted %s" % d)

    def get_json(self):
        return json.dumps(self.get_dictionary())

    def save_json(self):
        """
            Downloads and parses a PDF file from TAMU grade distributions, provides a JSON file with results
            Return value is pathlib object for the output JSON.
        """

        logging.info("Converting content to JSON...")
        # convert dictionary to json

        results_dict = self.get_dictionary()

        json_dir = parent_dir / pathlib.Path("json")
        json_dir.mkdir(parents=True, exist_ok=True)
        json_file = json_dir / pathlib.Path(self.file_name() + ".json")

        with open(json_file, 'w') as file:
            json.dump(results_dict, file, indent=4)

        logging.info("Saved to JSON!")
        return json_file


if __name__ == "__main__":
    pdf_json = PdfParser("engineering", 2016, "fall", store_pdfs=True)
    pdf_json.save_json()
