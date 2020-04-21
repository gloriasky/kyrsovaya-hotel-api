from flask import Flask, jsonify, send_file
from flask_restful import request
from flask_cors import CORS
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)

from waitress import serve

from src import users
from src.constants import *

import os, os.path, tempfile
import logging
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from queue import Queue

import time
from datetime import datetime, timedelta

import requests

app = Flask(__name__)
CORS(app, supports_credentials=True, expose_headers='Content-Disposition')
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY


def validate_permission(permission):
    users.validate_permission(get_jwt_identity(), permission)


@app.route('/api/validate_permission')
@jwt_required
def val_perm():
    try:
        permission = request.args.get('permission')
        validate_permission(permission)
        return 'granted!', 200, {'Cache-Control': 'no-cache'}
    except Exception as e:
        return 'Denied: ' + str(e), 400


@app.route('/welcome')
@jwt_required
def export():
    try:
        return {'message': 'Hello World!'}
    except Exception as e:
        return 'Failed to get stats: ' + str(e), 400


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        user = users.validate(data['login'].lower(), data['password'])
        user_view = users.user_view(user)
        data = {'jwt': create_jwt(identity=data['login'].lower()), 'user': user_view}
        if SECURITY_ALERT_ENABLED:
            # security_alert(get_user_ip(), login)
            print('Sending email')
        response = jsonify(data)

        expires = datetime.fromtimestamp(time.time() + 30 * 24 * 60 * 60)
        return response, 200
    except Exception as e:
        print(str(e))
        return 'Failed to login: ' + str(e), 400


@app.route('/api/user', methods=['POST'])
# @jwt_required
def create_user():
    try:
        json = request.json

        login, password = users.new(json['email'], **json)

        if REGISTRATION_EMAIL_ENABLED:
            print('Sending email')
            # registration_email(json['email'], json['firstName'], login, json['permissions'], id)

        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create user: ' + str(e), 400


if __name__ == "__main__":
    serve(app, port=5000)