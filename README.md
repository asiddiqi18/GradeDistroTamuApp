# TAMU Grade Distribution Database

![Website image showing courses panel!](https://i.imgur.com/rgc6jxS.png)

This project is a web application that allows users to view statistical breakdowns of grade distributions at Texas A&M University.

All grade records are obtained from Texas A&M's registrar in PDF format. This web app parses the PDF files using the PyPDF2 library and extracts the relevant information into either JSON or database format.

This application allows users to search for records by year, college, semester, and professor. You can view charts of a professor's history, including their average GPA breakdown and trends over time.

The application is built mostly in Python, using Flask as the web framework. SQL-Alchemy and SQLite are used for database management, and ChartJS is used for the interactive charts.

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
