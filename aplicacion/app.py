## Imports
from flask import Flask, render_template, redirect, url_for, request, abort,\
    session, jsonify
from flask_sqlalchemy import SQLAlchemy
from aplicacion import config
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required,\
    current_user
from bson import ObjectId
from flask_pymongo import PyMongo, ObjectId
from flask_cors import CORS, cross_origin
import os
import json
import logging
import requests

## Initialize
app = Flask(__name__)
app.config.from_object(config)

cors = CORS(app)
mongo = PyMongo(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

logging.basicConfig(filename='log/error.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/start')
def start():
    if current_user.is_authenticated:
        return redirect(url_for("hello_world"))
    else:
        return jsonify(message="It is neccesary to be logged."), 401


########## login part ##########

@app.route('/loginprueba')
def loginprueba():
    try:
        username=request.authorization["username"]
        password=request.authorization["password"]
    except Exception as e:
            print(e)
            return jsonify(error="Unauthenticated. Not basic auth send with username or password."), 401

    from aplicacion.models import Users, Projects
    user = Users.query.filter_by(username=username).first()
    if user is not None and user.verify_password(password):
        session.permanent = True
        login_user(user)
    return "Works"

@app.route('/login')
def login():
    # if current_user.is_authenticated:
    #     return jsonify(message="User already logged: " + current_user.username)

    try:
        username=request.authorization["username"]
        password=request.authorization["password"]
    except Exception as e:
            print(e)
            return jsonify(error="Unauthenticated. Not basic auth send with username or password."), 401

    from aplicacion.models import Users, Projects
    user = Users.query.filter_by(username=username).first()
    if user is not None and user.verify_password(password):
        session.permanent = True
        login_user(user)
        print(current_user)

        # userprojects = Projects.query.filter(Projects.users.any(id=user.id)).all()
        # nameprojects=""
        # for i,project in enumerate(userprojects):
        #     nameprojects+=project.name
        #     if i < len(userproject) - 1:
        #         nameprojects+=","
        userproject = Projects.query.filter(Projects.users.any(id=user.id)).first()

        url = "http://127.0.0.1:5000/loginprueba"
        headers = {
          'Authorization': 'Basic UHJ1ZWJhOjEyMw=='
        }
        prueba = requests.request("GET", url, headers=headers)
        print(prueba)

        response = jsonify(
                username=username,
                email=user.email,
                project=userproject.name,
                projectdescription=userproject.description,
                cookie=prueba.cookies.get('session'),
                set_cookie=prueba.headers.get('set-cookie')
                )
        return response
    else:
        return jsonify(error="Unauthenticated. Error in log in."), 401

@app.route("/logout")
def logout():
    logout_user()
    return jsonify(message="User has logout.")

@app.route('/changepassword', methods=['GET','PUT'])
@login_required
def changepassword():
    if not current_user.is_authenticated:
            return jsonify(error="Unauthenticated. Error in log in."), 401

    try:
        newpassword=request.headers['newpassword']
    except Exception as e:
            print(e)
            return jsonify(error="Unauthenticated. Not basic auth send with username or password."), 400

    from aplicacion.models import Users
    user = Users.query.filter_by(username=current_user.username).first()
    if user is not None:
        user.password = newpassword
        db.session.commit()
        return jsonify(message="Password change successfully.")
    else:
        return jsonify(error="Unauthenticated. Error in log in."), 401


########## dmps part ##########

@app.route('/dmps', methods=['GET'])
@login_required
def get_all_dmps():
    dmps = mongo.db.dmps.find()
    output = []
    for dmp in dmps:
        output.append(dmp)
    return JSONEncoder().encode(output)

#{ "user":"esteban","project":"street-spectra", "purpose":"collection of elements", "sharing":yes, "license":"cc-by"}

@app.route('/dmps', methods=['POST'])
@login_required
def post_dmp():
    try:
        data = request.get_json(force=True)
    except Exception as e:
            print(e)
            return jsonify(error="Failed to decode JSON object."), 400
    mongo.db.dmps.insert_one(data)
    return jsonify({'ok': True, 'message': 'DMP created successfully!'}), 201 


@app.route('/dmps/<dmp_id>', methods=['PUT'])
@login_required
def put_dmp(dmp_id):
    try:
        data = request.get_json(force=True)
    except Exception as e:
            print(e)
            return jsonify(error="Failed to decode JSON object."), 400
    mongo.db.dmps.update({"_id": ObjectId(dmp_id)}, {"$set": data})
    return jsonify({'ok': True, 'message': 'DMP updated successfully!'}), 200

@app.route('/dmps/<dmp_id>')
@login_required
def get_dmp(dmp_id):
    try:
        dmp = mongo.db.dmps.find_one({'_id': ObjectId(dmp_id)})
    except Exception as e:
            print(e)
            return jsonify(error="Not a correct dmp id format."), 400
    if dmp is None:
        return jsonify({'error': 'DMP ' + dmp_id + 'not found'}), 404
    return JSONEncoder().encode(dmp)


########## tasks part ##########

## Format task = {status, url, dmp}
## Stauts: pending, finished, error
## Example: {"status":"pending", "url":"nothingYet", "dmp":"1234"}

@app.route('/tasks', methods=['GET'])
@login_required
def get_all_tasks():
    status = request.args.get('status')
    if status is not None:
        tasks = mongo.db.tasks.find({'status':status})
    else:
        tasks = mongo.db.tasks.find()
    output = []
    for task in tasks:
        output.append(task)
    print (output)
    return JSONEncoder().encode(output)

@app.route('/task', methods=['POST'])
@login_required
def post_task():
    try:
        data = request.get_json(force=True)
    except Exception as e:
            print(e)
            return jsonify(error="Failed to decode JSON object."), 400
    mongo.db.tasks.insert_one(data)
    return jsonify({'ok': True, 'message': 'Task created successfully!'}), 201


########## Login manager part ##########

@login_manager.user_loader
def load_user(user_id):
    from aplicacion.models import Users
    return Users.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error':"Unauthorized. You need to log in first."}), 404

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'error':"Page not found..."}), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error':"Unauthorized"}), 401
