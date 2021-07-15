import requests
import pathlib
import re
import shelve
from PyPDF2 import PdfFileReader
import json
import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class PdfToJson:

    def __init__(self, college, year, semester, directory=None):
        if (directory is None):
            self.directory = pathlib.Path(__file__).parent.absolute()
        else:
            self.directory = directory
        self.college = college
        self.year = year
        self.semester = semester
        self.arg_expect_amount = 22
        self.semesters = {"spring": 1, "summer": 2, "fall": 3}
        self.json = None

    def get_college_abbreviation_map(self):
        abb_dir = self.directory / pathlib.Path("college_abbreviations.json")

        with open(str(abb_dir), 'r') as file:
            abbreviations = json.load(file)
            return abbreviations


    def name(self):
        return ("%s_%s_%s") % (self.college, self.year, self.semester)


    def download_pdf(self, college, year, semester):
        '''
            Downloads grade reports to current directory from web, if not already installed.
            Takes in file name as only parameter, saves PDF to 'working directory/pdf'
            Returns path of downloaded PDF / existing PDF
        '''

        abbreviation_dict = self.get_college_abbreviation_map()
        if college.lower() not in abbreviation_dict:
            raise ValueError("College '%s' not identified. Enter one of these following colleges: %s" % (college, ", ".join(list(abbreviation_dict.keys()))))
        if int(year) < 2016:
            raise ValueError("Data for years past 2016 do not exist!")

        if semester not in self.semesters:
            raise ValueError("Semester '%s' not identified. Enter one of the following semesters: %s" % ", ".join(self.semesters))
        
        abbreviation = abbreviation_dict[college.lower()]
        file_name = self.name() + ".pdf"
        year_semester = year + str(self.semesters[semester])

        url = 'https://web-as.tamu.edu/GradeReports/PDFReports/%s/grd%s%s.pdf' % (year_semester, year_semester, abbreviation)

        pdf_dir = self.directory / pathlib.Path("pdf")
        pdf_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = pdf_dir / pathlib.Path(file_name)

        if not pdf_path.exists():
            res = requests.get(url)
            res.raise_for_status()

            with open(pdf_path, 'wb') as f:
                f.write(res.content)
        
        return pdf_path


    def text_extractor(self, path):

        shelf_dir = self.directory / pathlib.Path("shelf")

        shelf_dir.mkdir(parents=True, exist_ok=True)

        shelf_file = shelf_dir / pathlib.Path(self.name())

        shelf = shelve.open(str(shelf_file))

        if 'data' in shelf:
            results = shelf['data']
            shelf.close()
            return results

        # TODO: 2016 no work
        regex = re.compile(r'(\D{4})-(\d{3})-(\d{3})\s+(\d+)\s+(\d+.\d+)%\s+(\d+)\s+(\d+.\d+)%\s+(\d+)\s+(\d+.\d+)%\s+(\d+)\s+(\d+.\d+)%\s+(\d+)\s+(\d+.\d+)%\s+(\d+)\s+(\d+.\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S+\s\w)')
        with open(path, 'rb') as f:
            pdf = PdfFileReader(f)
            # get the first page
            number_of_pages = pdf.getNumPages()
            
            results = []

            for p in range(number_of_pages):
                page = pdf.getPage(p)
                text = page.extractText()
                regex_result = regex.findall(text)
                if (regex_result is None):
                    print("%d is none" % p)
                else:
                    results.extend(regex_result)

            shelf['data'] = results
            shelf.close()
            return results


    def _courses_list_to_json(self, list_of_courses):
        if (len(list_of_courses) == 0):
            logging.warn("No courses were found.")
            return None

        results_dict = {}

        for result in list_of_courses:

            if (len(result) != self.arg_expect_amount):
                raise RuntimeError("Incorrect number of attributes in course info. Got %d, expected %d.", len(result), self.arg_expect_amount)

            department = result[0]
            course = result[1]
            section = result[2]

            grade_amount = {}
            grade_amount['A'] = result[3]
            grade_amount['B'] = result[5]
            grade_amount['C'] = result[7]
            grade_amount['D'] = result[9]
            grade_amount['F'] = result[11]

            grade_percentage = {}
            grade_percentage['A'] = result[4]
            grade_percentage['B'] = result[6]
            grade_percentage['C'] = result[8]
            grade_percentage['D'] = result[10]
            grade_percentage['F'] = result[12]

            total = result[13]
            gpa = result[14]

            other = {}
            other['I'] = result[15]
            other['S'] = result[16]
            other['U'] = result[17]
            other['Q'] = result[18]
            other['X'] = result[19]
            other['total'] = result[20]

            professor = result[21]


            section_dict = {
                "grade_amount": grade_amount,
                "grade_percentage": grade_percentage,
                "total": total,
                "gpa": gpa,
                "other": other,
                "professor": professor
            }

            if (department not in results_dict):
                results_dict[department] = {}
            if (course not in results_dict[department]):
                results_dict[department][course] = {}

            results_dict[department][course][section] = section_dict

        return results_dict   


    def clean(self):

        import shutil
        dir_names = ["shelf", "json", "pdf"]
        for dir in dir_names:
            dir_path = self.directory / pathlib.Path(dir)
            if dir_path.is_dir():
                folder = str(dir_path)
                shutil.rmtree(folder)
                logging.info("Successfully deleted %s" % dir)


    def save_json(self):
        '''
            Downloads and parses a PDF file from TAMU grade distributions, returns JSON file containing info.
        '''

        logging.info("Downloading PDF...")

        pdf_path = self.download_pdf(self.college, self.year, self.semester)

        logging.info("Extracting content from PDF...")
        results = self.text_extractor(pdf_path)
        logging.info("Converting content to JSON...")

        logging.info("Saving JSON to file...")
        json_obj = self._courses_list_to_json(results)
        json_dir = self.directory / pathlib.Path("json")
        json_dir.mkdir(parents=True, exist_ok=True)
        json_file = json_dir / pathlib.Path(self.name() + ".json")
        with open(json_file, 'w') as file:
            json.dump(json_obj, file, indent=4)

        logging.info("Saved to JSON!")

        self.json = json_obj


    def get_json_obj(self):
        if self.json is None:
            self.save_json()
        return self.json


    def get_list_of_lists(self):
        logging.info("Downloading PDF...")

        pdf_path = self.download_pdf(self.college, self.year, self.semester)

        logging.info("Extracting content from PDF...")
        results = self.text_extractor(pdf_path)
        
        return results

if __name__ == "__main__":
    pdf_json = PdfToJson("engineering", "2021", "spring")
    pdf_json.save_json()

