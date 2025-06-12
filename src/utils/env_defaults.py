import os
from typing import Any


def set(k: str, v: Any):
    os.environ.setdefault(k, str(v))


def set_env_defaults():
    set("PORT", 45003)
    set("MAX_WORKERS", 5)
    set("RESULTS_DIR", "submission_results")
    set("MOCK_BUILD_HANDLER", False)
    set("DATA_PATH", "data")
    set("DATASET_PATH", os.path.join(os.environ["DATA_PATH"], "dataset.json"))
    set("ARCHIVES_ROOT", os.path.join(os.environ["DATA_PATH"], "archives"))
