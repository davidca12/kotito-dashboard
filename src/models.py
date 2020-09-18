import requests
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class SchoolManager():

    @staticmethod
    def getSchools():
        res = requests.get('http://us-central1-thinkinghatwonder.cloudfunctions.net/getSchools')

        x = res.json()

        print("Github's status is currently:--------->", x[0]['schoolCode'])  

        kotokan_code=""
        name1=""


        for i in range(len(x)):
            for c,v in x[i].items():
                if c=="schoolCode" and v!="": 
                    
                    kotokan_code=v
                
                    #print(kotokan_id1)
                elif c=="name" and v!="":
                    name1=v
                    #print(name1)
            school1=School(name=name1,kotokan_id=kotokan_code)
            db.session.add(school1)    
        db.session.commit()



class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kotokan_id = db.Column(db.String(120), unique=True, nullable=False)
    name= db.Column(db.String(120), unique=True, nullable=False)

    #relacion uno a muchos con estudiantes.
    students = db.relationship('Student', lazy=True)
   
    #relacion
    users = db.relationship('User', lazy=True)


    def __repr__(self):
        return '<School %r>' % self.name
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            " kotokan_id":self. kotokan_id
            # do not serialize the password, its a security breach
        }




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(120), unique=True, nullable=False)
    last_name=db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    #relacion con cursos 1 to many
    courses = db.relationship('Course', lazy=True)

    #relacion con la school de uno a muchos
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    school = db.relationship("School") 

    def __repr__(self):
        return '<User %r>' % self.name
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
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
   
    
    # created_at = db.Column(db.DateTime(), nullable=False, default=db.func.current_timestamp()) no se si lo utlizaremos

    def __repr__(self):
        return '<Course %r>' % self.id
   

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    kotokan_id = db.Column(db.String(120), unique=True, nullable=False)

    #relacion con el user de 1 to many
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


class StudentManager():
    @staticmethod
    def getStudents():
        student={
                "gameStatus": 45,
                "age": "44",
                "id": "1uuo9IBzDQaMOZoHevha",
                "grade": "12",
                "name": "test nuevo",
                "avatar":{
                    "static": "https://firebasestorage.googleapis.com/v0/b/thinkinghatwonder-eu/o/images%2Favatars%2FJolia_1.png?alt=media&token=8030ea96-07b3-44d8-abfe-e084251e8857",
                    "gif": "https://firebasestorage.googleapis.com/v0/b/thinkinghatwonder-eu/o/images%2Favatars%2FJolia_1.gif?alt=media&token=369f7ce6-7b83-4a3a-8ac1-3cd89741b52d"
                }
            }
        school1 = School(
        name = "hola",
        kotokan_id = "1",
        ) 
        db.session.add(school1)
        db.session.commit()

        
        student1 = Student(name=student["name"], avatar=student["avatar"], game_status= student["gameStatus"],kotokan_id=student["id"],school_id=1)
        db.session.add(student1)
        db.session.commit()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    #last_name= db.Column(db.String(120), unique=True, nullable=False)
    avatar = db.Column(db.String(255), unique=True, nullable=False)

    game_status = db.Column(db.Text, nullable=False)
    

    kotokan_id = db.Column(db.String(120), unique=True, nullable=False)

    #esto marca la relacion que tengo con la school de unos a muchos
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    school = db.relationship("School") 
    
    
    #relacion muchos a muchos
    courses = db.relationship("Course", secondary=enrollment, back_populates="students")
    def __repr__(self):
        return '<Student %r>' % self.name
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "game_status": self.game_status,
            "avatar":self.avatar
        }


    