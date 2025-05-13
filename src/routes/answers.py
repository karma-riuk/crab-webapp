# routes/answers.py
from flask import Blueprint, request, jsonify, current_app
from utils.errors import InvalidJsonFormatError
from utils.process_data import evaluate_comments
import json

router = Blueprint('answers', __name__, url_prefix='/answers')

ALLOWED_EXT = {'json'}


def validate_json_format(data: str) -> dict[str, str]:
    try:
        obj = json.loads(data)
        if not isinstance(obj, dict):
            raise InvalidJsonFormatError("Submitted json doesn't contain an object")
        if not all(isinstance(v, str) for v in obj.values()):
            raise InvalidJsonFormatError(
                "Submitted json object must only be str -> str. Namely id -> comment"
            )
        return obj
    except InvalidJsonFormatError as e:
        raise e
    except Exception:
        raise InvalidJsonFormatError()


@router.route('/submit/comments', methods=['POST'])
def submit_comments():
    file = request.files.get('file')
    if file is None or file.filename is None or file.filename.split('.')[-1] not in ALLOWED_EXT:
        return jsonify({'error': 'Only JSON files are allowed'}), 400
    data = file.read().decode()
    try:
        validated = validate_json_format(data)
    except InvalidJsonFormatError as e:
        return jsonify({'error': 'Invalid JSON format', 'message': str(e)}), 400

    socketio = current_app.extensions['socketio']
    sid = request.headers.get('X-Socket-Id')
    if sid:
        socketio.emit('successful-upload', room=sid)
        socketio.emit('started-processing', room=sid)

    results = evaluate_comments(
        validated, lambda p: socketio.emit('progress', {'percent': p}, room=sid)
    )
    return jsonify(results)


@router.route('/submit/refinement', methods=['POST'])
def submit_refinement():
    file = request.files.get('file')
    # similar to above
    return jsonify({'message': 'Answer submitted successfully'})
