from flask import Flask, request, jsonify
from flask_uuid import FlaskUUID

import json
import uuid
import datetime

fileSys = None
app = Flask(__name__)

def start(fileSystem):
    global app, fileSys
    
    FlaskUUID(app)

    app.run(debug=True, use_reloader=False)
    fileSys = fileSystem

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/v1/auth/token', methods=['POST'])
def auth_token():
    #req#{"data":{"type":"token","attributes":{"username":"b@a.c","password":"casac"}}}

    #json = request.get_json()
    #username = json.data.attributes.username
    #password = json.data.attributes.password

    token = {
        "data": {
            "id": str(uuid.uuid4()),
            "type": "token",
            "attributes": {
                "expires_in": 863999,
                "refresh_token": str(uuid.uuid4()),
                "provider": "husqvarna",
                "user_id": str(uuid.uuid4()),
                "scope": "iam:read iam:write"
            }
        }
    }

    return jsonify(token)

@app.route('/v1/features')
def features_list():
    pass

@app.route('/v1/devices')
def devices_list():
    pass

@app.route('/v1/devices/<uuid:id>')
def device():
    device = {
        "id": id,
        "name": "TODO",
        "description": "TODO",
        "category": "",
        "configuration_synchronized": True,
        "configuration_synchronized_v2": {
            "value": True,
            "timestamp": ""
        },
        "abilities": [],
        "scheduled_events": [],
        "settings": []
    }
    return device

@app.route('/v1/locations')
def locations_list():
    pass

@app.route('/v1/activations')
def activations_list():
    pass
    

 