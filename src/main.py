"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Teacher, School, Student,StudentManager,SchoolManager

import requests

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
    #SchoolManager.getSchools()
    StudentManager.getStudents()
    return generate_sitemap(app)

@app.route('/schools', methods=['GET'])
def all_school():

    schools= School.query.all()
    all_schools= list(map(lambda x: x.serialize(), schools))


    return jsonify(all_schools), 200

@app.route('/schools/<int:school_id>', methods=['GET'])
def school_data(school_id):

    school= School.query.get(school_id)
    
    return jsonify(school.serialize()), 200

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


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
