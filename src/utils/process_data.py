# utils/process_data.py
import json
import sys
from .paths import get_project_path
from sacrebleu import sentence_bleu as bleu


def build_reference_map(dataset_path: str) -> dict[str, list[str]]:
    ref_map = {}
    data = json.loads(open(dataset_path).read())
    for entry in data['entries']:
        id_ = entry['metadata']['id']
        comments = entry['comments']
        ref_map[id_] = [c['body'] for c in comments]
    return ref_map


REFERENCE_MAP = build_reference_map(str(get_project_path('../data/dataset.json')))


def evaluate_comments(answers: dict[str, str], percent_cb):
    total = len(answers)
    results = {}
    for i, (id_, gen) in enumerate(answers.items(), 1):
        if id_ not in REFERENCE_MAP:
            print(f'id: "{id_}" is not present in the dataset', file=sys.stderr)
            continue
        paraphrases = REFERENCE_MAP[id_]
        max_score = 0.0
        scores = []
        for p in paraphrases:
            score = bleu(gen, [p]).score
            scores.append(score)
            max_score = max(max_score, score)
        results[id_] = {'max_bleu_score': max_score, 'bleu_scores': scores, 'proposed_comment': gen}
        percent_cb(int(i / total * 100))
    return results


def evaluate_refinement(answers: dict[str, str], percent_cb):
    total = len(answers)
    for i, (key, value) in enumerate(answers.items(), 1):
        print(f"Processing {key}: {value}...")
        # time.sleep(1)
        print("Done")
        percent_cb(int(i / total * 100))
