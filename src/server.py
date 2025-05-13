# server.py
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from routes.index import router as index_router
from routes.answers import router as answers_router
from routes.datasets import router as datasets_router

import os

app = Flask(__name__, static_folder='../public', static_url_path='/')
CORS(app)

# Register routes
app.register_blueprint(index_router)        # serves '/' and '/api/hello'
app.register_blueprint(answers_router)      # mounts at '/answers'
app.register_blueprint(datasets_router)     # mounts at '/datasets'


def init_socketio(app):
    socketio = SocketIO(app, cors_allowed_origins='*')

    @socketio.on('connect')
    def _():
        print('Websocket client connected')

    return socketio


# Init socketio
socketio = init_socketio(app)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    socketio.run(app, port=port)
