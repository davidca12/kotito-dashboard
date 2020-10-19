import os
from dotenv import load_dotenv

import requests
import json
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

API_HOST = os.getenv('API_HOST')
API_TOKEN= os.getenv('API_TOKEN')


class StageManager():
    @staticmethod
    def getStage():
        url =f"{API_HOST}/getStages"
        headers = {
            'Authorization': API_TOKEN ,
            'Content-Type' : 'application/json'
        }

        response = requests.post(url, headers=headers)
        result = response.json()

        for stageKoto in result["stages"]:
            stage = {
                "kotokan_id": 0,
                "content": {},
                "levels" : []
            }
            
            stage["content"] = {
                "header" : stageKoto["stage"]["content"]["en"]["header"], 
                "name" : stageKoto["stage"]["content"]["en"]["name"]
            } 
            stage["kotokan_id"] = stageKoto["stage"]["id"]

            if len(stageKoto["levels"]) == 0 :
                continue

            for levelKoto in stageKoto["levels"]:
                problemCount = len(levelKoto["problems"])
                stage["levels"].append({ "problemCount" : problemCount, "id" : levelKoto["level"]["id"] })

            row = Stage.query.filter_by(kotokan_id = stageKoto["stage"]["id"]).first()

            if row:
                row.content = json.dumps(stage["content"]) 
                row.levels = json.dumps(stage["levels"])
                db.session.commit()
            else:
                row = Stage(
                    kotokan_id= stage["kotokan_id"],
                    content =json.dumps(stage["content"]), 
                    levels = json.dumps(stage["levels"])
                )
                db.session.add(row)
                db.session.commit()
                
 
            

class SchoolManager():
    @staticmethod
    def getSchools():

        url =f"{API_HOST}/getSchools"
    

        headers = {
            'Authorization': API_TOKEN ,
            'Content-Type' : 'application/json'
        }

        response = requests.request("POST", url , headers=headers)
        result = response.json()

        for school in result:
            row = School.query.filter_by(kotokan_id=school["schoolCode"]).first()
            
            if not row:
                row = School(
                    kotokan_id=school["schoolCode"],
                    name= school["name"],
                )
                db.session.add(row)
                db.session.commit()
            TeachersManager.getTeachers(row) 
                
class TeachersManager():
    @staticmethod
    def getTeachers(school):

        payload = {"schoolCode": school.kotokan_id}

        #payload= f"{schoolCode: {kotokan_code}}"
        url =f"{API_HOST}/getTeachersBySchoolCode"
        headers = {
            'Authorization': API_TOKEN ,
            'Content-Type' : 'application/json'
        }

        response = requests.post( url , headers=headers, data= json.dumps(payload))
        result = response.json()
        
        for teacher in result:
            row = Teacher.query.filter_by(kotokan_id=teacher["id"]).first()
            
            if not row:
                row = Teacher(
                    kotokan_id=teacher["id"],
                    name= teacher["firstName"],
                    lastName=teacher["lastName"],
                    email=teacher["email"],
                    languaje=teacher["language"],
                    school_id=school.id
                )
                db.session.add(row)
                db.session.commit()
            StudentManager.getStudents(row,school.kotokan_id,school.id)
                    
class StudentManager():
    @staticmethod
    def getStudents(teacher,schoolCode,schooldId):
        #json a string [] arraylista, {}objeto,diccionario
        #"accountId": teacher.kotokan_id, 
                
        payload = {"accountId": teacher.kotokan_id,"schoolCode" : schoolCode}

        #payload= f"{schoolCode: {kotokan_code}}"
        url =f"{API_HOST}/getPlayersBySchoolCode"
        headers = {
            'Authorization': API_TOKEN ,
            'Content-Type' : 'application/json'
        }

        #loads: string a json / dumps: json a string

        response = requests.post( url , headers=headers, data= json.dumps(payload))
        result = response.json()

        result_string=json.dumps(result)
        result_json = json.loads(result_string)

        # """ print(type(result))
        # print(len(result))
        # print(result[0])
        # print(result[0]["name"]) """

        
        for student in result:
            # print("avatar" in student.keys())
            avatar = "avatar" in student.keys()
            name = "name" in student.keys()
            gameStatus = "gameStatus" in student.keys()
            kotokanId = "id" in student.keys()

            if avatar == False:
                student["avatar"] = "Empty"
                # print(student["avatar"])

            if name == False:
                student["name"] = "Anonimous"
                # print(student["name"])
            
            if gameStatus == False:
                student["gameStatus"] = "Not information"
                # print(student["gameStatus"])
            
            if kotokanId == False:
                student["id"] = "Anonimous"
                # print(student["id"])

            row = Student.query.filter_by(kotokan_id=student["id"]).first()

            if not row:
                row = Student(
                    kotokan_id=student["id"],
                    name= student["name"],
                    avatar=json.dumps(student["avatar"]),
                    game_status=json.dumps(student["gameStatus"]),
                    school_id=schooldId,
                    teacher_id=teacher.id
                )
                db.session.add(row)
                db.session.commit()

class SignInKotokanService():

    @staticmethod
    def login_in(email, password):
        url = API_HOST + '/login'
        myobj = {'email': email, 'password': password}
        response = requests.post(url, data = myobj)
        parsed_data = response.json()
        message = parsed_data['message']
        data = parsed_data['data']
        return response.status_code==200, message, data

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kotokan_id = db.Column(db.String(120), unique=True, nullable=False)
    name= db.Column(db.String(120), unique=False, nullable=False)
   
    #relacion uno a muchos con los profesores
    teachers = db.relationship('Teacher', lazy=True)

    #relacion uno a muchos con los estudiatnes
    students = db.relationship('Student', lazy=True)

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
    kotokan_id = db.Column(db.String(80))
    name= db.Column(db.String(120), unique=False, nullable=False)
    lastName= db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    languaje= db.Column(db.String(120), unique=False, nullable=False)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    
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
            "email":self.email
            # do not serialize the password, its a security breach
        }


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    avatar = db.Column(db.Text, nullable=False)
    game_status = db.Column(db.Text, nullable=False)
    kotokan_id = db.Column(db.String(120), unique=True, nullable=False)


    #esto marca la relacion que tengo con el profesor de unos a muchos
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    teacher = db.relationship("Teacher")

    #esto marca la relacion que tengo con la school de unos a muchos
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    school = db.relationship("School")     
     

    def __repr__(self):
        return '<Student %r>' % self.name
    def serialize(self):
        
        game_status_json=json.loads(self.game_status)
        avatar_json=json.loads(self.avatar) 

        return {
            "id": self.id,
            "name": self.name,
            "game_status": game_status_json,
            "avatar": avatar_json
        }


class Stage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kotokan_id= db.Column(db.Integer, unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    levels = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Stage %r>' % self.kotokan_id
    def serialize(self):

        content_json=json.loads(self.content)
        levels_json=json.loads(self.levels) 
        return {
            "content": content_json,
            "levels": levels_json,
            "kotokan_id" : self.kotokan_id
        } 
    
    





