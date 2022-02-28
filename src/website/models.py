from enum import unique

from sqlalchemy.orm import backref
from . import db


# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_creating_table.htm


class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college = db.Column(db.String(50))
    year = db.Column(db.SmallInteger)
    semester = db.Column(db.String(16))
    department = db.Column(db.String(4))
    course = db.Column(db.String(4))
    section = db.Column(db.SmallInteger)
    amount_A = db.Column(db.SmallInteger, default=0)
    percent_A = db.Column(db.Numeric(precision=2))
    amount_B = db.Column(db.SmallInteger, default=0)
    percent_B = db.Column(db.Numeric(precision=2))
    amount_C = db.Column(db.SmallInteger, default=0)
    percent_C = db.Column(db.Numeric(precision=2))
    amount_D = db.Column(db.SmallInteger, default=0)
    percent_D = db.Column(db.Numeric(precision=2))
    amount_F = db.Column(db.SmallInteger, default=0)
    percent_F = db.Column(db.Numeric(precision=2))
    total_A_F = db.Column(db.SmallInteger)
    gpa = db.Column(db.Numeric)
    other_I = db.Column(db.SmallInteger)
    other_S = db.Column(db.SmallInteger)
    other_U = db.Column(db.SmallInteger)
    other_Q = db.Column(db.SmallInteger)
    other_X = db.Column(db.SmallInteger)
    other_total = db.Column(db.SmallInteger)
    instructor = db.Column(db.String(50))
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'))

    def __init__(self):
        self.amount_A = 0
        self.amount_B = 0
        self.amount_C = 0
        self.amount_D = 0
        self.amount_F = 0
        self.total_A_F = 0
        self.other_Q = 0

    def merge(self, other):
        self.amount_A += other.amount_A
        self.amount_B += other.amount_B
        self.amount_C += other.amount_C
        self.amount_D += other.amount_D
        self.amount_F += other.amount_F
        self.other_Q += other.other_Q
        self.total_A_F += other.total_A_F

    def retrieve_percents(self):
        total = self.total_A_F
        self.percent_A = self.amount_A / total
        self.percent_B = self.amount_B / total
        self.percent_C = self.amount_C / total
        self.percent_D = self.amount_D / total
        self.percent_F = self.amount_F / total

    def __repr__(self):
        return f'''<Grades: [
            College: {self.college} Year: {self.year},  Semester: {self.semester},  Department: {self.department},  Course: {self.course},  GPA: {self.gpa}, Instructor: {self.instructor}]>'''


class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(50))
    full_name = db.Column(db.String(50))
    classes = db.relationship('Grades', backref='professor')

    def __repr__(self):
        return f'''<Professor: [
            id: {self.id}
            short_name: {self.short_name}, 
            full_name: {self.full_name}, 
            classes: {self.classes}, 
            ]>'''
