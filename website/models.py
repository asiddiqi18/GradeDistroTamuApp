from . import db 

# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_creating_table.htm

class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(4))
    course = db.Column(db.String(4))
    section = db.Column(db.SmallInteger)
    amount_A = db.Column(db.SmallInteger)
    percent_A = db.Column(db.Numeric)
    amount_B = db.Column(db.SmallInteger)
    percent_B = db.Column(db.Numeric)
    amount_C = db.Column(db.SmallInteger)
    percent_C = db.Column(db.Numeric)
    amount_D = db.Column(db.SmallInteger)
    percent_D = db.Column(db.Numeric)
    amount_F = db.Column(db.SmallInteger)
    percent_F = db.Column(db.Numeric)
    total_A_F = db.Column(db.SmallInteger)
    gpa = db.Column(db.Numeric)
    other_I = db.Column(db.SmallInteger)
    other_S = db.Column(db.SmallInteger)
    other_U = db.Column(db.SmallInteger)
    other_Q = db.Column(db.SmallInteger)
    other_X = db.Column(db.SmallInteger)
    other_total = db.Column(db.SmallInteger)
    instructor = db.Column(db.String(50))
