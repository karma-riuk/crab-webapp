# routes/datasets.py
from flask import Blueprint, send_from_directory, request, jsonify
import os

router = Blueprint('datasets', __name__, url_prefix='/datasets')

DATASETS = {'comment_generation', 'code_refinement'}

# below, the '../' + is need because the send_from send_from_directory is local
# the file, but the DATA_DIR is local to the root of the repo
DATA_DIR = os.path.join('..', os.getenv("DATA_PATH", "data"))


@router.route('/download/<dataset>')
def download(dataset):
    if dataset not in DATASETS:
        return jsonify({'error': 'Invalid dataset name'}), 400
    with_ctx = request.args.get('withContext', 'false').lower() == 'true'
    fname = f"{dataset}_{'with_context' if with_ctx else 'no_context'}.zip"
    return send_from_directory(DATA_DIR, fname, as_attachment=True)
