# routes/datasets.py
from flask import Blueprint, send_from_directory, request, jsonify
from utils.paths import get_project_path

router = Blueprint('datasets', __name__, url_prefix='/datasets')

DATASETS = {'comment_generation', 'code_refinement'}
DATA_DIR = get_project_path('../data')


@router.route('/download/<dataset>')
def download(dataset):
    if dataset not in DATASETS:
        return jsonify({'error': 'Invalid dataset name'}), 400
    with_ctx = request.args.get('withContext', 'false').lower() == 'true'
    fname = f"{dataset}_{'with_context' if with_ctx else 'no_context'}.zip"
    return send_from_directory(DATA_DIR, fname, as_attachment=True)
