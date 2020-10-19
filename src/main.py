"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, make_response 
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Teacher, School, Student, StudentManager, SchoolManager, TeachersManager, SignInKotokanService, StageManager, Stage
import requests

#Token and login
from werkzeug.security import generate_password_hash, check_password_hash
import uuid 
import jwt
import datetime
from functools import wraps
#

#from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    SchoolManager.getSchools()
    StageManager.getStage()

    #StudentManager.getStudents(11,"oi0ztsj1sBPvSvWUgMvyK2SEnrF3","testCode",6)

    #TeachersManager.getTeachers()
    return generate_sitemap(app)

def token_required(f):  
    @wraps(f)  
    def decorator(*args, **kwargs):
        token = None 
        kotokan_access_token = None
        if 'x-access-tokens' in request.headers:  
            token = request.headers['x-access-tokens'] 
        print(token)
        if not token:  
            return jsonify({'message': 'a valid token is missing'})   

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            print("@@data", data)
            kotokan_access_token = data['accessToken']
            print("@@koto",kotokan_access_token)
            current_teacher = Teacher.query.filter_by(id=data['id']).first()
            print("@@current",current_teacher)

        except: 
            return jsonify({'message': 'token is invalid'})
          
        return f(current_teacher, *args,  **kwargs)
    return decorator

@app.route('/register', methods=['GET', 'POST'])
def signup_user():
    data = request.get_json()  

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_teacher = Teacher(public_id=str(uuid.uuid4()), name=data['name'],email=data["email"],password=hashed_password, admin=False,school_id=1) 
    db.session.add(new_teacher)  
    db.session.commit()    

    return jsonify({'message': 'registered successfully'})

@app.route('/login', methods=['GET', 'POST'])  
def login_user():
    auth = request.authorization

    print("#####################",auth)

    if not auth or not auth.username or not auth.password:  
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
    
    result, message, data = SignInKotokanService.login_in(auth.username,auth.password) 

   

    if result:
        teacher = Teacher.query.filter_by(email=auth.username).first()
        if not(teacher):
            teacher = Teacher(name=data['user']['firstName'],email=data['user']["email"], admin=False,school_id= data['user']['schoolCode'],kotokan_id=data['user']['id'],lastName=data['user']['lastName'],languaje=data['user']['language'])
            db.session.add(teacher)
            db.session.commit()

        token = jwt.encode({'id': teacher.id, 'accessToken': data['user']['accessToken'],'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('Not possible to log in',  401, {'msg': message})

@app.route('/schools', methods=['GET'])
def all_school():

    schools= School.query.all()
    all_schools= list(map(lambda x: x.serialize(), schools))


    return jsonify(all_schools), 200

@app.route('/schools/<int:school_id>', methods=['GET'])
def school_data(school_id):

    school= School.query.get(school_id)
    
    return jsonify(school.serialize()), 200

@app.route('/teachers/<int:teacher_id>/students', methods=['GET'])
def teacher_and_students_data12(teacher_id):
    teacher = Teacher.query.get(teacher_id) 
    studentsList = list(map(lambda student: student.serialize(), teacher.students))
    #return 'received'
    return jsonify(studentsList), 200

@app.route('/students', methods=['GET'])
@token_required
def teacher_and_students_data(teacher):

    studentFound = Student.query.filter_by(school_id=teacher.school_id)

    studentsList = list(map(lambda student: student.serialize(), studentFound ))
    #return 'received'
    return jsonify(studentsList), 200

""" @app.route('/students', methods=['GET'])
@token_required
def teacher_and_students_data(teacher):
    studentsList = list(map(lambda student: student.serialize(), teacher.students))
    #return 'received'
    return jsonify(studentsList), 200"""


@app.route('/teachers/<int:teacher_id>', methods=['GET'])
def teacher_data(teacher_id):

    teacher= Teacher.query.get(teacher_id)
    
    return jsonify(teacher.serialize()), 200
    

@app.route('/teachers', methods=['GET'])
def handle_hello():

    teachers= Teacher.query.all()
    all_teachers= list(map(lambda x: x.serialize(), teachers))
    
    return jsonify(all_teachers), 200
       
@app.route('/students/<int:student_id>', methods=['GET']) 
def student_data(student_id):

    student= Student.query.get(student_id)
    
    return jsonify(student.serialize()), 200

@app.route('/students', methods=['GET']) 
def all_student_data():

    student= Student.query.all()
    all_students= list(map(lambda x: x.serialize(), student))
    
    return jsonify(all_students), 200

@app.route('/stages', methods=['GET']) 
def all_stages():

    stage= Stage.query.all()
    all_stages= list(map(lambda x: x.serialize(), stage))
    
    return jsonify(all_stages), 200

@app.route('/stages/<int:stage_id>', methods=['GET']) 
def stage(stage_id):

    stage= Stage.query.get(stage_id)

    return jsonify(stage.serialize()), 200





# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
