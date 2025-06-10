# routes/index.py
from flask import Blueprint, jsonify, current_app


router = Blueprint('index', __name__)


@router.route('/')
def welcome():
    return current_app.send_static_file('index.html')


@router.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello from the backend!'})
