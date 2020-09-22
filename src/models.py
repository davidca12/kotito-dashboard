import requests
import json
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class SchoolManager():
    @staticmethod
    def getSchools():
        res = requests.get('http://us-central1-thinkinghatwonder.cloudfunctions.net/getSchools')
        x = res.json()

        kotokan_code=""
        name1=""

        for i in range(len(x)):
            for c,v in x[i].items():
                if c=="schoolCode" and v!="": 
                    kotokan_code=v
                elif c=="name" and v!="":
                    name1=v
            school1=School(name=name1,kotokan_id=kotokan_code)
            db.session.add(school1)    
        db.session.commit()


class StudentManager():
    @staticmethod
    def getStudents():
        #json a string
        response=json.dumps(
            {
                "name":"dsadsadasdas",
                "avatar": "erase una vez y adios y adios adioassaaaaaa",
                "id": "unicosss",    
                "gameStatus": {
                    "stage": {
                    "1": {
                        "countHachi": 4,
                        "level": {
                        "1": {
                            "problem": {
                            "1": {
                                "completed": True,
                                "difficulty": {
                                "1": {
                                    "completed": True,
                                    "playCount": 1,
                                    "started": True,
                                    "points": 55,
                                    "id": 1
                                },
                                "2": {
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 1,
                                    "completed": False
                                },
                                "3": {
                                    "completed": False,
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 1
                                },
                                "4": {
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 1,
                                    "completed": False
                                }
                                }
                            },
                            "2": {
                                "completed": True,
                                "difficulty": {
                                "1": {
                                    "completed": False,
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 2
                                },
                                "2": {
                                    "playCount": 1,
                                    "started": True,
                                    "points": 94,
                                    "id": 2,
                                    "completed": True
                                },
                                "3": {
                                    "completed": False,
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 2
                                },
                                "4": {
                                    "completed": False,
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 2
                                }
                                }
                            },
                            "3": {
                                "difficulty": {
                                "1": {
                                    "completed": False,
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 3
                                },
                                "2": {
                                    "completed": False,
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 3
                                },
                                "3": {
                                    "playCount": 0,
                                    "started": True,
                                    "points": 0,
                                    "id": 3,
                                    "completed": False
                                },
                                "4": {
                                    "completed": False,
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 3
                                }
                                }
                            },
                            "4": {
                                "difficulty": {
                                "1": {
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 4,
                                    "completed": False
                                },
                                "2": {
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 4,
                                    "completed": False
                                },
                                "3": {
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 4,
                                    "completed": False
                                },
                                "4": {
                                    "completed": False,
                                    "playCount": 0,
                                    "started": False,
                                    "points": 0,
                                    "id": 4
                                }
                                }
                            }
                            }
                        }
                        }
                    }
                    }
                }, 
            }
        )
        student = json.loads(response) #string a json
        gamestatusText = json.dumps(student['gameStatus'])

        #school = School.all().first
        #print (school)
        """
        school1 = School(
        name = "dadadgdggdsdaasgggaa",
        kotokan_id = "25842",
        
        ) 
        db.session.add(school1)
        db.session.commit()
        """

        teacher1 = Teacher(
        name = "dadadgdggdsdaasgggaa",
        email="pepito@gmail.com",
        school_id=1
        ) 
        db.session.add(teacher1)
        db.session.commit()
        

        #school1 = db.session.query(School).first()

        student1 = Student(name=student["name"], avatar=student["avatar"], game_status= gamestatusText,kotokan_id=student["id"],teacher_id=1)
        print ("adioss---------->>>>>>>>>>>>>>>>",gamestatusText)

        print(student1)
        
        db.session.add(student1)
        db.session.commit()
       




class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kotokan_id = db.Column(db.String(120), unique=True, nullable=False)
    name= db.Column(db.String(120), unique=False, nullable=False)
   
    #relacion uno a muchos
    teachers = db.relationship('Teacher', lazy=True)

    def __repr__(self):
        return '<School %r>' % self.name
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            " kotokan_id":self. kotokan_id
            # do not serialize the password, its a security breach
        }


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    
    #relacion con la school de uno a muchos
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    school = db.relationship("School") 

    #relacion un profesor con muchos estudiantes
    students = db.relationship('Student', lazy=True)

    def __repr__(self):
        return '<Teacher %r>' % self.name
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            # do not serialize the password, its a security breach
        }


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    avatar = db.Column(db.String(255), unique=False, nullable=False)
    game_status = db.Column(db.Text, nullable=False)
    kotokan_id = db.Column(db.String(120), unique=True, nullable=False)


    #esto marca la relacion que tengo con la school de unos a muchos
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    teacher = db.relationship("Teacher")     

    def __repr__(self):
        return '<Student %r>' % self.name
    def serialize(self):

        game_status_json=json.loads(self.game_status)
        return {
            "id": self.id,
            "name": self.name,
            "game_status": game_status_json,
            "avatar":self.avatar
        }



