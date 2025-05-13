# utils/paths.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_project_path(relative_path: str) -> Path:
    return PROJECT_ROOT / relative_path
