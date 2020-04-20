from flask import Flask, jsonify, send_file
from flask_restful import request
from flask_cors import CORS
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)

from waitress import serve

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

@app.route('/welcome')
def export():
    try:
        return {'message': 'Hello World!'}
    except Exception as e:
        return 'Failed to get stats: ' + str(e), 400


if __name__ == "__main__":
    serve(app, port=5000)