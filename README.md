# TAMU Grade Distribution Database

This project is a web application to view statistical breakdowns of grade distributions at Texas A&M University. 

All records of grades are obtained from [Texas A&M's registrar](https://web-as.tamu.edu/GradeReports/) in PDF formats.

This website is able to parse through the PDF files and convert them into plain text and extract the needed information into either JSON format or database format.

The parsing of PDF files was achieved through the [PyPDF2](https://pypi.org/project/PyPDF2/) library for Python. This library was able to parse the PDFs correctly, but they lost all formatting during the process. A regex pattern was used to reformat and extract all relevant information.

This application is able to search records by year, college, semester, and professor. You can view charts of a professor's history, including their average GPA breakdown and trends across the years.


Most of this project is in Python, and Flask was used as the web framework. SQL-Alchemy and SQLite were used for database management, and ChartJS were used for the interactive charts.

Try the website here:


https://tamu-grades.herokuapp.com/

Note, since this website is using a free cloud service, Heroku, the initial loading of this website may be delayed.

Most records have entries, however, the registrar does not offer entries for the ones listed in the tables below.

### The following parameters do not have PDFs on record:

| College  | Year | Semester |
| ------------- |:-------------:|:-------------:|
|academic success center | 2020 | summer
|academic success center | 2017 | summer
|school of law (undergraduate & graduate) | 2020 | spring
|school of law (undergraduate & graduate) | 2018 | spring, summer
|school of law (undergraduate & graduate) | 2017 | spring
|medicine (undergraduate & graduate) | 2020 | spring
|medicine (undergraduate & graduate) | 2019 | summer
|military science | 2017 | summer
|academic success center | 2016 | spring, summer
|associate provost for undergraduate programs | 2016 | spring, summer
|school of law (undergraduate & graduate) | 2016 | spring, summer, fall


### The following parameters have PDFs but those PDFs are malformed:
| College  | Year | Semester |
| ------------- |:-------------:|:-------------:|
|academic success center | 2018 | summer
|medicine (undergraduate & graduate) | 2019 | spring
|military science | 2020 | summer
|military science | 2019 | summer
|military science | 2018 | summer
