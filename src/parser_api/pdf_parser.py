import requests
import pathlib
import re
import shelve
from PyPDF2 import PdfFileReader
import json
import logging
import shutil

# Get the directory this file is in, as pathlib object.
parent_dir = pathlib.Path(__file__).parent.absolute()


def get_colleges():
    """ From college_abbreviations.json, retrieve mapping of colleges to abbreviations as JSON. """
    abb_dir = parent_dir / pathlib.Path("college_abbreviations.json")
    with open(str(abb_dir), 'r') as file:
        abbreviations = json.load(file)
        return abbreviations


class PdfParser:
    """ API to parse PDFs from the grade distribution registrar """

    # Setup logging for debugging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    # Currently disabled
    # logging.disable(logging.INFO)

    # Regex to extract info from PDF binaries.
    # regex_main is used for most retrievals
    regex_main = re.compile(
        r'(\D{4})-(\d{3,4})-(\d{3})\s+(\d+)\s+(\d+.\d+)%\s+(\d+)\s+(\d+.\d+)%\s+(\d+)\s+(\d+.\d+)%\s+(\d+)\s+('
        r'\d+.\d+)%\s+(\d+)\s+(\d+.\d+)%\s+(\d+)\s+(\d+.\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+('
        r'\S+\s\w)')

    # However, most PDFs from 2016 are formatted slightly different, requiring an alternative pattern
    regex_alt = re.compile(
        r'(\D{4})-(\d{3,4})-(\d{3})\s+(\d+.\d+)\s+(\S+\s\w)\s(\d+.\d+)%\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+('
        r'\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+.\d+)%\s+(\d+.\d+)%\s+(\d+.\d+)%\s+(\d+.\d+)%')

    def __init__(self, college, year, semester, store_pdfs=False):
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
            raise ValueError("College '%s' not identified. Enter one of these following colleges: %s" % (
                self.college, ", ".join(list(abbreviation_dict.keys()))))
        if int(self.year) < 2016:
            raise ValueError("Data for years before 2016 do not exist!")
        if self.semester not in self.semesters:
            raise ValueError(
                "Semester '%s' not identified".join(self.semesters))

    def file_name(self):
        """ Generate a safe file name for the PDF from the parameters """
        filename = "%s_%s_%s" % (self.college, self.year, self.semester)
        dangerous_chars = [' ', '/']
        for danger in dangerous_chars:
            filename = filename.replace(danger, "_")
        return filename

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

        # Get/create directory for PDFs, and get path of the pdf that will be downloaded/is saved
        file_name = self.file_name() + ".pdf"
        pdf_dir = parent_dir / pathlib.Path("pdf")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = pdf_dir / pathlib.Path(file_name)

        # If PDF not already downloaded, then request it from URL
        if not pdf_path.exists():
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

        # save the path of the PDF as a field
        self.pdf_path = pdf_path

    def text_extractor(self):
        """
            Parses the grade distribution PDF for its information using regex pattern.
            Returns a 2D list, structured in a tabular way.
            What index corresponds to what value depends on the type of pattern used.
        """

        # If this function is called without downloading the PDF first, then download the PDF
        if self.pdf_path is None:
            logging.info("No PDF file has been downloaded. Downloading now...")
            self.download_pdf()

        # Otherwise, use regex pattern to extract information
        # Regex patterns precompiled above.
        results = []
        with open(self.pdf_path, 'rb') as f:
            pdf = PdfFileReader(f)
            number_of_pages = pdf.getNumPages()

            for p in range(number_of_pages):
                page = pdf.getPage(p)
                text = page.extractText()
                regex_result = self.regex_main.findall(text)
                # If this regex pattern did not yield anything, then try using the alternative regex pattern
                if len(regex_result) == 0:
                    regex_result = self.regex_alt.findall(text)
                    if len(regex_result) != 0:
                        self.alt = True  # Designate that alternative pattern was used for future uses

                # Append all results to a master list
                results.extend(regex_result)

        # Depending on setting put in constructor, delete PDF from computer after extracting its text
        if not self.store_pdfs:
            pathlib.Path.unlink(self.pdf_path)
        return results

    def get_dictionary(self):
        """ Serializes the PDF results to Python dictionary object """
        list_of_courses = self.text_extractor()
        if len(list_of_courses) == 0:
            logging.warn("No courses were found.")
            return None

        results_dict = {}

        for result in list_of_courses:

            if len(result) != self.arg_expect_amount:
                raise RuntimeError("Incorrect number of attributes in course info. Got %d, expected %d.", len(result),
                                   self.arg_expect_amount)

            department = result[0]
            course = result[1]
            section = result[2]

            grade_amount = {}
            grade_percentage = {}
            other = {}
            total = None
            gpa = None
            professor = None

            if not self.alt:
                grade_amount['A'] = result[3]
                grade_amount['B'] = result[5]
                grade_amount['C'] = result[7]
                grade_amount['D'] = result[9]
                grade_amount['F'] = result[11]
                grade_percentage['A'] = result[4]
                grade_percentage['B'] = result[6]
                grade_percentage['C'] = result[8]
                grade_percentage['D'] = result[10]
                grade_percentage['F'] = result[12]
                total = result[13]
                gpa = result[14]
                other['I'] = result[15]
                other['S'] = result[16]
                other['U'] = result[17]
                other['Q'] = result[18]
                other['X'] = result[19]
                other['total'] = result[20]
                professor = result[21]
            else:
                grade_amount['A'] = result[6]
                grade_amount['B'] = result[7]
                grade_amount['C'] = result[8]
                grade_amount['D'] = result[9]
                grade_amount['F'] = result[10]
                grade_percentage['A'] = result[5]
                grade_percentage['B'] = result[18]
                grade_percentage['C'] = result[19]
                grade_percentage['D'] = result[20]
                grade_percentage['F'] = result[21]
                total = result[11]
                gpa = result[3]
                other['I'] = result[12]
                other['S'] = result[13]
                other['U'] = result[14]
                other['Q'] = result[15]
                other['X'] = result[16]
                other['total'] = result[17]
                professor = result[4]

            section_dict = {
                "grade_amount": grade_amount,
                "grade_percentage": grade_percentage,
                "total": total,
                "gpa": gpa,
                "other": other,
                "professor": professor
            }

            if department not in results_dict:
                results_dict[department] = {}
            if course not in results_dict[department]:
                results_dict[department][course] = {}

            results_dict[department][course][section] = section_dict

        return results_dict

    @staticmethod
    def clean():
        """ Static method to delete all local files related to this API. Useful for testing. """
        dir_names = ["json", "pdf"]
        for dir in dir_names:
            dir_path = parent_dir / pathlib.Path(dir)
            if dir_path.is_dir():
                folder = str(dir_path)
                shutil.rmtree(folder)
                logging.info("Successfully deleted %s" % dir)

    def save_json(self):
        """
            Downloads and parses a PDF file from TAMU grade distributions, provides a JSON file with results
            Return value is pathlib object for the output JSON.
        """

        if self.json is None:
            self.get_json_obj()

        json_dir = parent_dir / pathlib.Path("json")
        json_dir.mkdir(parents=True, exist_ok=True)
        json_file = json_dir / pathlib.Path(self.file_name() + ".json")
        with open(json_file, 'w') as file:
            json.dump(self.json, file, indent=4)

        logging.info("Saved to JSON!")
        return json_file

    def get_json_obj(self):
        """ Get JSON object of data """
        results = self.text_extractor()

        logging.info("Converting content to JSON...")
        # convert dictionary to json
        self.json = json.dumps(self.get_dictionary(), indent=4)
        return self.json


if __name__ == "__main__":
    pdf_json = PdfParser("engineering", "2021", "spring")
    pdf_json.save_json()
