from . import db


class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college = db.Column(db.String(50))
    year = db.Column(db.SmallInteger)
    semester = db.Column(db.String(16))
    department = db.Column(db.String(4))
    course = db.Column(db.String(4))
    section = db.Column(db.SmallInteger)
    amount_a = db.Column(db.SmallInteger, default=0)
    percent_a = db.Column(db.Numeric(precision=2))
    amount_b = db.Column(db.SmallInteger, default=0)
    percent_b = db.Column(db.Numeric(precision=2))
    amount_c = db.Column(db.SmallInteger, default=0)
    percent_c = db.Column(db.Numeric(precision=2))
    amount_d = db.Column(db.SmallInteger, default=0)
    percent_d = db.Column(db.Numeric(precision=2))
    amount_f = db.Column(db.SmallInteger, default=0)
    percent_f = db.Column(db.Numeric(precision=2))
    total = db.Column(db.SmallInteger)
    gpa = db.Column(db.Numeric)
    other_i = db.Column(db.SmallInteger)
    other_s = db.Column(db.SmallInteger)
    other_u = db.Column(db.SmallInteger)
    other_q = db.Column(db.SmallInteger)
    other_x = db.Column(db.SmallInteger)
    other_total = db.Column(db.SmallInteger)
    professor = db.Column(db.String(50))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))

    def __init__(self):
        self.amount_a = 0
        self.amount_b = 0
        self.amount_c = 0
        self.amount_d = 0
        self.amount_f = 0
        self.total = 0
        self.other_q = 0

    def merge(self, other):
        self.amount_a += other.amount_a
        self.amount_b += other.amount_b
        self.amount_c += other.amount_c
        self.amount_d += other.amount_d
        self.amount_f += other.amount_f
        self.other_q += other.other_q
        self.total += other.total

    def retrieve_percents(self):
        total = self.total
        self.percent_a = self.amount_a / total
        self.percent_b = self.amount_b / total
        self.percent_c = self.amount_c / total
        self.percent_d = self.amount_d / total
        self.percent_f = self.amount_f / total

    def __repr__(self):
        return f'''<Grades: [
            College: {self.college} Year: {self.year},  Semester: {self.semester},  Department: {self.department}, 
            Course: {self.course},  GPA: {self.gpa}, Professor: {self.professor}]>'''


class GradesMultiple(Grades):

    def __init__(self, other: [Grades]):
        super().__init__()

        self.total_gpa_year = {}
        self.total_courses_year = {}

        self.total_gpa = 0
        self.total_courses = 0

        self.courses_taught = set()

        if not other:
            return

        self.professor = other[0].professor
        for x in other:
            self.add(x)

        self.set_percents()
        self.gpa = self.total_gpa / self.total_courses

    def add(self, other: Grades):
        self.amount_a += other.amount_a
        self.amount_b += other.amount_b
        self.amount_c += other.amount_c
        self.amount_d += other.amount_d
        self.amount_f += other.amount_f
        self.other_q += other.other_q
        self.courses_taught.add(f"{other.department} {other.course}")
        self.total_courses_year[other.year] = self.total_courses_year.get(other.year, 0) + 1
        self.total_gpa += other.gpa
        self.total_courses += 1
        self.total += other.total
        self.total_gpa_year[other.year] = self.total_gpa_year.get(other.year, 0) + other.gpa

    def set_percents(self):
        self.percent_a = self.amount_a / self.total
        self.percent_b = self.amount_b / self.total
        self.percent_c = self.amount_c / self.total
        self.percent_d = self.amount_d / self.total
        self.percent_f = self.amount_f / self.total

    def sorted_years_and_gpa(self):
        avg_dict = {year: float(self.total_gpa_year[year] / self.total_courses_year[year]) for year in
                    self.total_gpa_year.keys()}

        years = list(avg_dict.keys())
        gpa_list = list(avg_dict.values())

        zipped_lists = zip(*sorted(zip(years, gpa_list)))
        return [list(tup) for tup in zipped_lists]


class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(50))
    full_name = db.Column(db.String(50))
    classes = db.relationship('Grades', backref='instructor')

    def __repr__(self):
        return f'''<Professor: [
            id: {self.id}
            short_name: {self.short_name}, 
            full_name: {self.full_name}, 
            classes: {self.classes}, 
            ]>'''
