# routes/answers.py
from threading import Thread
from flask import Blueprint, request, jsonify, current_app, url_for
from utils.errors import InvalidJsonFormatError
from utils.process_data import evaluate_comments, evaluate_refinement
from utils.observer import SocketObserver, Status, Subject, request2status
import functools
import json, uuid

router = Blueprint('answers', __name__, url_prefix='/answers')

ALLOWED_EXT = {'json'}


def validate_json_format_for_comment_gen(data: str) -> dict[str, str]:
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


def validate_json_format_for_code_refinement(data: str) -> dict[str, dict[str, str]]:
    try:
        obj = json.loads(data)
        if not isinstance(obj, dict):
            raise InvalidJsonFormatError("Submitted json doesn't contain an object")

        for _, submission in obj.items():
            if not all(isinstance(content, str) for content in submission.values()):
                raise InvalidJsonFormatError(
                    "Submitted json object must be str -> {str -> str}. Namely id -> {filename -> content of file}"
                )
        return obj

    except InvalidJsonFormatError as e:
        raise e
    except Exception:
        raise InvalidJsonFormatError()


@router.route('/submit/comment', methods=['POST'])
def submit_comments():
    file = request.files.get('file')
    if file is None or file.filename is None or file.filename.split('.')[-1] not in ALLOWED_EXT:
        return jsonify({'error': 'Only JSON files are allowed'}), 400
    data = file.read().decode()
    try:
        validated = validate_json_format_for_comment_gen(data)
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


socket2observer = {}


@router.route('/submit/refinement', methods=['POST'])
def submit_refinement():
    file = request.files.get('file')
    if file is None or file.filename is None or file.filename.split('.')[-1] not in ALLOWED_EXT:
        return jsonify({'error': 'Only JSON files are allowed'}), 400
    data = file.read().decode()
    try:
        validated = validate_json_format_for_code_refinement(data)
    except InvalidJsonFormatError as e:
        return jsonify({'error': 'Invalid JSON format', 'message': str(e)}), 400

    socketio = current_app.extensions['socketio']
    sid = request.headers.get('X-Socket-Id')
    socket_emit = functools.partial(socketio.emit, room=sid)

    process_id = str(uuid.uuid4())
    subject = Subject(process_id, evaluate_refinement)
    request2status[process_id] = subject

    if sid:
        socket_emit('successful-upload')
        socket_emit('started-processing')
        obs = SocketObserver(socket_emit)
        socket2observer[sid] = obs
        subject.registerObserver(obs)

    subject.launch_task(validated)
    url = url_for(f".status", id=process_id, _external=True)
    return jsonify(
        {
            "id": process_id,
            "status_url": url,
            "help_msg": "Check the status of this process at /answers/status/<id>. Once the evaluation is complete, a call to this URL will return the results.",
        }
    )


@router.route('/status/<id>')
def status(id):
    if id not in request2status:
        return jsonify({"error": "Id doens't exist", "message": f"Id {id} doesn't exist"}), 404

    subject = request2status[id]
    if subject.status == Status.COMPLETE:
        return jsonify({"status": "complete", "results": subject.results})
    elif subject.status == Status.PROCESSING:
        socketio = current_app.extensions['socketio']
        sid = request.headers.get('X-Socket-Id')
        socket_emit = functools.partial(socketio.emit, room=sid)

        request2status[id] = subject
        if sid:
            if sid in socket2observer:
                return (
                    jsonify(
                        {
                            "error": "Already listening",
                            "message": f"You are already seeing the real-time progress of that request, please don't spam",
                        }
                    ),
                    400,
                )

            obs = SocketObserver(socket_emit)
            socket2observer[sid] = obs
            obs.updatePercentage(subject.percent)
            subject.registerObserver(obs)
        return jsonify({"status": "processing", "percent": subject.percent})
    elif subject.status == Status.CREATED:
        return jsonify({"status": "created"})

    raise Exception("This code should be unreachable")
