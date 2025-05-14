import os
import sys, docker
from utils.handlers import get_build_handler
from .paths import get_project_path
from sacrebleu import sentence_bleu as bleu
from utils.dataset import ArchiveState, Dataset

REFERENCE_MAP = Dataset.from_json(
    str(get_project_path('../data/dataset.json'))
).build_reference_map()

ARCHIVES_ROOT = str(get_project_path('../data/archives'))

DOCKER_CLIENT = docker.from_env()


def evaluate_comments(answers: dict[str, str], percent_cb):
    total = len(answers)
    results = {}
    for i, (id_, gen) in enumerate(answers.items(), 1):
        if id_ not in REFERENCE_MAP:
            print(f"[WARNING] skipping {id} since it is not present in dataset", file=sys.stderr)
            continue
        entry = REFERENCE_MAP[id_]
        max_score = 0
        scores = []
        for p in [entry.comments[0].body] + entry.comments[0].paraphrases:
            score = round(bleu(gen, [p]).score, 2)
            scores.append(score)
            max_score = max(max_score, score)

        results[id_] = {
            'max_bleu_score': max_score,
            'bleu_scores': scores,
            'proposed_comment': gen,
        }
        percent_cb(int(i / total * 100))
    return results


def evaluate_refinement(answers: dict[str, dict[str, str]], percent_cb):
    total = len(answers)
    results = {}
    for i, (id, changes) in enumerate(answers.items(), 1):
        print(f"[INFO] Processing {id} ({i}/{total}: {i/total:.2%})...")
        if id not in REFERENCE_MAP:
            print(f"[WARNING] skipping {id} since it is not present in dataset", file=sys.stderr)
            continue
        entry = REFERENCE_MAP[id]
        print(f"[INFO] {id} info: {entry.metadata.repo} #PR {entry.metadata.pr_number}")
        try:
            build_handler = get_build_handler(
                ARCHIVES_ROOT, entry.metadata.archive_name(ArchiveState.MERGED)
            )
            build_handler.set_client(DOCKER_CLIENT)
        except Exception as e:
            print(
                f"[ERROR] {id} ({entry.metadata.repo} #PR {entry.metadata.pr_number}) {type(e)}: {e}",
                file=sys.stderr,
            )
            continue

        for file_path, change in changes.items():
            full_path = os.path.join(build_handler.path, file_path)
            print("[INFO] Writing change to file:", full_path)
            dirname = os.path.dirname(full_path)
            if not os.path.exists(dirname):
                print("[INFO] Creating directory:", dirname)
                os.makedirs(dirname)
            with open(full_path, "w") as f:
                f.write(change)

        results[id] = {}
        with build_handler:
            steps = [
                ("compilation", build_handler.compile_repo),
                ("test", build_handler.test_repo),
            ]
            for task, action in steps:
                try:
                    print(f"[INFO] Executing {task}...")
                    action()
                    print(f"[INFO] {task} executed successfully on {id}")
                    results[id][task] = True
                except Exception as e:
                    results[id][task] = False
                    print(
                        f"[ERROR] {id} ({entry.metadata.repo} #PR {entry.metadata.pr_number}) {type(e)}: {e}",
                        file=sys.stderr,
                    )
                    break

        print(f"[INFO] Done with {id}...")
        percent_cb(int(i / total * 100))

    return results
