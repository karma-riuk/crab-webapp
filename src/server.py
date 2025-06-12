from utils.env_defaults import set_env_defaults
from dotenv import load_dotenv

set_env_defaults()
load_dotenv()

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
from utils.observer import Status, Subject, SocketObserver
from routes.index import router as index_router
from routes.answers import QUEUE_MANAGER, router as answers_router
from routes.datasets import router as datasets_router
from werkzeug.exceptions import HTTPException
import os

app = Flask(__name__, static_folder='../public', static_url_path='/')

with app.app_context():
    Subject.setup()

CORS(app)

# Register routes
app.register_blueprint(index_router)        # serves '/' and '/api/hello'
app.register_blueprint(answers_router)      # mounts at '/answers'
app.register_blueprint(datasets_router)     # mounts at '/datasets'


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        response = {
            "error": e.name.lower().replace(" ", "_"),  # e.g. "not_found"
            "message": e.description,
        }
        return app.json.response(response), e.code or 500

    app.logger.exception(e)
    return (
        app.json.response({"error": "internal_server_error", "message": str(e)}),
        500,
    )


def init_socketio(app):
    socketio = SocketIO(app, cors_allowed_origins='*')

    @socketio.on('connect')
    def on_connect():
        print('Websocket client connected')

    @socketio.on('disconnect')
    def on_disconnect():
        print('Websocket client disconnected')
        sid = request.sid   # type: ignore
        if sid in SocketObserver.socket2obs:
            obs = SocketObserver.socket2obs.pop(sid)
            if obs in Subject.obs2subject:
                subject = Subject.obs2subject[obs]
                subject.unregisterObserver(obs)

    @socketio.on('get_queue_position')
    def on_get_queue_position(data):
        sid = request.sid   # type: ignore
        subject_id = data["id"]
        subject = Subject.id2subject[subject_id]
        if subject.status == Status.WAITING:
            return socketio.emit(
                'queue_position',
                {"status": "waiting", "position": QUEUE_MANAGER.get_position(subject_id)},
                to=sid,
            )
        return socketio.emit('queue_position', {"status": subject.status.value}, to=sid)

    return socketio


# Init socketio
socketio = init_socketio(app)

if __name__ == '__main__':
    port = int(os.environ['PORT'])
    socketio.run(
        app,
        use_reloader=True,
        host="0.0.0.0",
        port=port,
    )
