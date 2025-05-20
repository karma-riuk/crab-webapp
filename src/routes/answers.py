# routes/answers.py
from typing import Callable
from flask import Blueprint, request, jsonify, current_app, url_for
from utils.errors import InvalidJsonFormatError
from utils.process_data import evaluate_comments, evaluate_refinement
from utils.observer import SocketObserver, Status, Subject
import functools
import json

from utils.queue_manager import QueueManager

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


QUEUE_MANAGER = QueueManager(1)


def handler(type_: str, validate_json: Callable, evaluate_submission: Callable):
    file = request.files.get('file')
    if file is None or file.filename is None or file.filename.split('.')[-1] not in ALLOWED_EXT:
        return jsonify({'error': 'Only JSON files are allowed'}), 400
    data = file.read().decode()
    try:
        validated = validate_json(data)
    except InvalidJsonFormatError as e:
        return jsonify({'error': 'Invalid JSON format', 'message': str(e)}), 400

    subject = Subject(type_, evaluate_submission)
    process_id = subject.id
    Subject.id2subject[process_id] = subject

    QUEUE_MANAGER.submit(subject, validated)
    url = url_for(f".status", id=process_id, _external=True)
    return jsonify(
        {
            "id": process_id,
            "status_url": url,
            "help_msg": "Check the status of this process at /answers/status/<id>. Once the evaluation is complete, a call to this URL will return the results.",
        }
    )


@router.route('/submit/<any(comment, refinement):task>', methods=['POST'])
def submit_comments(task):
    if task == "comment":
        validator = validate_json_format_for_comment_gen
        evaluator = evaluate_comments
    else:
        validator = validate_json_format_for_code_refinement
        evaluator = evaluate_refinement

    return handler(task, validator, evaluator)


@router.route('/status/<id>')
def status(id):
    if id not in Subject.id2subject:
        return jsonify({"error": "Id doens't exist", "message": f"Id {id} doesn't exist"}), 404

    subject = Subject.id2subject[id]
    if subject.status == Status.COMPLETE:
        return jsonify({"status": "complete", "type": subject.type, "results": subject.results})

    socketio = current_app.extensions['socketio']
    sid = request.headers.get('X-Socket-Id')
    socket_emit = functools.partial(socketio.emit, to=sid)

    if sid and sid in SocketObserver.socket2obs:
        obs = SocketObserver.socket2obs[sid]
        subject_watched_by_socket = Subject.obs2subject[obs]
        if subject == subject_watched_by_socket:
            return (
                jsonify(
                    {
                        "error": "Already listening",
                        "message": f"You are already seeing the real-time progress of that request, please don't spam",
                    }
                ),
                400,
            )

        subject_watched_by_socket.unregisterObserver(obs)
        SocketObserver.socket2obs.pop(sid)
        socket_emit("changing-subject")

    if subject.status == Status.PROCESSING:
        if sid:
            obs = SocketObserver(sid, socket_emit)
            obs.updatePercentage(subject.percent)
            subject.registerObserver(obs)
        return jsonify({"status": "processing", "percent": subject.percent})

    if subject.status == Status.WAITING:
        if sid:
            obs = SocketObserver(sid, socket_emit)
            subject.registerObserver(obs)
        return jsonify({"status": "waiting", "queue_position": QUEUE_MANAGER.get_position(id)})

    if subject.status == Status.CREATED:
        return jsonify({"status": "created"})

    raise Exception("This code should be unreachable")
