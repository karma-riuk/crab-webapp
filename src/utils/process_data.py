import sys

from utils.handlers import get_build_handler
from .paths import get_project_path
from sacrebleu import sentence_bleu as bleu
from utils.dataset import ArchiveState, Dataset

REFERENCE_MAP = Dataset.from_json(
    str(get_project_path('../data/dataset.json'))
).build_reference_map()

ARCHIVES_ROOT = str(get_project_path('../data/archives'))


def evaluate_comments(answers: dict[str, str], percent_cb):
    total = len(answers)
    results = {}
    print(REFERENCE_MAP.keys())
    for i, (id_, gen) in enumerate(answers.items(), 1):
        if id_ not in REFERENCE_MAP:
            print(f'id: "{id_}" is not present in the dataset', file=sys.stderr)
            continue
        entry = REFERENCE_MAP[id_]
        max_score = 0
        scores = []
        for p in [entry.comments[0].body] + entry.comments[0].paraphrases:
            score = round(bleu(gen, [p]).score, 2)
            scores.append(score)
            max_score = max(max_score, score)

        print(scores)
        results[id_] = {
            'max_bleu_score': max_score,
            'bleu_scores': scores,
            'proposed_comment': gen,
        }
        percent_cb(int(i / total * 100))
    return results


def evaluate_refinement(answers: dict[str, str], percent_cb):
    total = len(answers)
    for i, (key, value) in enumerate(answers.items(), 1):
        print(f"Processing {key}: {value}...")
        # time.sleep(1)
        print("Done")
        percent_cb(int(i / total * 100))
