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

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        serialize_dict = {
            'id': self.id,
            'college': self.college,
            'year': self.year,
            'semester': self.semester,
            'department': self.department,
            'course': self.course,
            'section': self.section,
            'amount_a': self.amount_a,
            'percent_a': self.percent_a,
            'amount_b': self.amount_b,
            'percent_b': self.percent_b,
            'amount_c': self.amount_c,
            'percent_c': self.percent_c,
            'amount_d': self.amount_d,
            'percent_d': self.percent_d,
            'amount_f': self.amount_f,
            'percent_f': self.percent_f,
            'total': self.total,
            'gpa': self.gpa,
            'other_i': self.other_i,
            'other_s': self.other_s,
            'other_u': self.other_u,
            'other_q': self.other_q,
            'other_x': self.other_x,
            'other_total': self.other_total,
            'professor': self.professor,
            'instructor_id': self.instructor_id
        }

        return {u: str(v) for u, v in serialize_dict.items()}

    @property
    def serialize_many2many(self):
        """
       Return object's relations in easily serializable format.
       NB! Calls many2many's serialize property.
       """
        return [item.serialize for item in self.many2many]

    def __repr__(self):
        return f'''<Grades: [
            College: {self.college} Year: {self.year},  Semester: {self.semester},  Department: {self.department}, 
            Course: {self.course},  GPA: {self.gpa}, Professor: {self.professor}]>'''


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
