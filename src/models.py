from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(120), unique=True, nullable=False)
    last_name=db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    #relacion
    courses = db.relationship('Course', lazy=True)
    def __repr__(self):
        return '<User %r>' % self.username
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
enrollment = db.Table('enrollment',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), unique=True, primary_key=False),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), unique=True, primary_key=False)
)
class Enrollment(db.Model):
    __tablename__ = "enrollment"
    __table_args__ = {'extend_existing': True} 
    id = db.Column('id', db.Integer, primary_key=True)
    game_statuses = db.relationship('GameStatus', lazy=True)
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    kotokan_id = db.Column(db.String(120), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")
    students = db.relationship("Student", secondary=enrollment, back_populates="courses")
    def __repr__(self):
        return '<Course %r>' % self.name
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    last_name= db.Column(db.String(120), unique=True, nullable=False)
    kotokan_id = db.Column(db.String(120), unique=True, nullable=False)
    #relacion muchos a muchos
    courses = db.relationship("Course", secondary=enrollment, back_populates="students")
    def __repr__(self):
        return '<Student %r>' % self.name
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name
        }
class GameStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kotokan_id = db.Column(db.String(120), unique=True, nullable=False)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'), nullable=False)
    enrollment = db.relationship("Enrollment")
    def __repr__(self):
        return '<GameStatus %r>' % self.id
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }