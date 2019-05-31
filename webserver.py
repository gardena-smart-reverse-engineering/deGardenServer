from flask import Flask, request, jsonify
from flask_uuid import FlaskUUID

import json
import datetime
from deGardenaWebservice import deGardenaWebservice

webservice = None
app = Flask(__name__)

def start(fileSystem):
    global app, webservice
    
    webservice = deGardenaWebservice(fileSystem)

    FlaskUUID(app)
    app.run(debug=True, use_reloader=False)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/v1/auth/token', methods=['POST'])
def auth_token():
    #req#{"data":{"type":"token","attributes":{"username":"b@a.c","password":"casac"}}}

    #json = request.get_json()
    #username = json.data.attributes.username
    #password = json.data.attributes.password
 
    return jsonify(webservice.auth_token("", ""))

@app.route('/v1/features')
def features():
    pass

@app.route('/v1/devices/<uuid:id>')
def device(id):
    return jsonify(webservice.device(id))

@app.route('/v1/devices')
def devices():
    return jsonify(webservice.devices())

@app.route('/v1/locations')
def locations():
    pass

@app.route('/v1/activations')
def activations():
    pass
    

 