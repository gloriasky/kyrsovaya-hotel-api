from flask import Flask, jsonify, send_file
from flask_restful import request
from flask_cors import CORS
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)

from waitress import serve

from src import employees as users
from src.constants import *

import os, os.path, tempfile
import logging
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from queue import Queue

import time
from datetime import datetime, timedelta

import requests
from src.hotel import hotel

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


@app.route('/api/rooms')
def get_rooms():
    try:
        return jsonify(hotel.get_rooms())
    except Exception as e:
        return 'Denied: ' + str(e), 400


@app.route('/api/services')
def get_services():
    try:
        filter = request.args.get('filter')
        return jsonify(hotel.get_services(filter))
    except Exception as e:
        return 'Denied: ' + str(e), 400


@app.route('/api/employees')
@jwt_required
def get_employees():
    try:
        validate_permission('admin')
        return jsonify(users.get_all_employees())
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
        user = users.validate_password(data['login'].lower(), data['password'])
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
        json['permissions'] = ['guest']

        login, password = users.new(json['email'], **json)

        if REGISTRATION_EMAIL_ENABLED:
            print('Sending email')
            # registration_email(json['email'], json['firstName'], login, json['permissions'], id)

        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create user: ' + str(e), 400


@app.route('/api/add/room', methods=['POST'])
@jwt_required
def create_room():
    try:
        print('Adding new room...')
        validate_permission('admin')
        json = request.json

        hotel.add_room(json)
        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/delete/room')
@jwt_required
def delete_room():
    try:
        print('Deleting room...')
        validate_permission('admin')
        _id = request.args.get('_id')

        hotel.delete_room(_id)
        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/get/room')
@jwt_required
def get_room():
    try:
        print('Getting room info...')

        _id: str = request.args.get('id')
        room: dict = hotel.get_room(_id)
        return jsonify(room), 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/get/image')
def get_image():
    try:
        search_query = request.args.get('search')

        return send_file(search_query, mimetype='image/gif',as_attachment=True)
    except Exception as e:
        return 'Failed to download results: ' + str(e), 400


@app.route('/api/update/room', methods=['POST'])
@jwt_required
def update_room():
    try:
        print('Adding new room...')
        validate_permission('admin')
        json: dict = request.json
        _id: str = request.args.get('id')

        hotel.update_room(_id, json)
        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/upload/image', methods=['POST'])
@jwt_required
def upload_image():
    try:
        validate_permission('admin')
        files = request.files
        path = request.args.get('path')
        if len(files) > 0:
            try:
                for name, file in files.items():
                    path = os.path.join(path, name)
                    file.save(path)

            except Exception as e:
                return 'Failed to process files: ' + str(e), 400

        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/add/service', methods=['POST'])
@jwt_required
def create_service():
    try:
        print('Adding new service...')
        validate_permission('admin')
        json = request.json

        hotel.add_service(json)
        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/delete/service')
@jwt_required
def delete_service():
    try:
        print('Deleting room...')
        validate_permission('admin')
        _id = request.args.get('_id')

        hotel.delete_service(_id)
        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/get/service')
@jwt_required
def get_service():
    try:
        print('Getting room info...')

        _id: str = request.args.get('id')
        service: dict = hotel.get_service(_id)
        return service, 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/update/service', methods=['POST'])
@jwt_required
def update_service():
    try:
        print('Adding new room...')
        validate_permission('admin')
        json: dict = request.json
        _id: str = request.args.get('id')

        hotel.update_service(_id, json)
        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/add/employee', methods=['POST'])
@jwt_required
def create_employee():
    try:
        print('Adding new employee...')
        validate_permission('admin')
        json = request.json

        users.add_employee(json)
        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/delete/employee')
@jwt_required
def delete_employee():
    try:
        print('Deleting employee...')
        validate_permission('admin')
        _id = request.args.get('_id')

        users.delete_employee(_id)
        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/get/employee')
@jwt_required
def get_employee():
    try:
        print('Getting employee info...')

        _id: str = request.args.get('id')
        employee: dict = users.get_employee(_id)
        return employee, 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


@app.route('/api/update/employee', methods=['POST'])
@jwt_required
def update_employee():
    try:
        print('Adding new room...')
        validate_permission('admin')
        json: dict = request.json
        _id: str = request.args.get('id')

        users.update_employee(_id, json)
        return 'Success', 200
    except Exception as e:
        print(str(e))
        return 'Failed to create room: ' + str(e), 400


if __name__ == "__main__":
    serve(app, port=5000)