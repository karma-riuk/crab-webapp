import sys
from typing_extensions import Callable
from utils.build_handlers import get_build_handler
from .paths import get_project_path
from sacrebleu import sentence_bleu as bleu
from utils.dataset import ArchiveState, Dataset

REFERENCE_MAP = Dataset.from_json(
    str(get_project_path('../data/dataset.json'))
).build_reference_map()

ARCHIVES_ROOT = str(get_project_path('../data/archives'))


def evaluate_comments(
    answers: dict[str, str],
    percent_cb: Callable[[float], None] = lambda _: None,
    complete_cb: Callable[[dict], None] = lambda _: None,
):
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

    complete_cb(results)
    return results


def evaluate_refinement(
    answers: dict[str, dict[str, str]],
    percent_cb: Callable[[float], None] = lambda _: None,
    complete_cb: Callable[[dict], None] = lambda _: None,
):
    n_answers = len(answers)
    n_steps = 4   # creating build handler + injecting the files in the repo + compilation + testing
    total_number_of_steps = n_answers * n_steps
    current_progress = 0
    results = {}
    for i, (id, changes) in enumerate(answers.items()):
        print(f"[INFO] Processing {id} ({i}/{n_answers}: {i/n_answers:.2%})...")
        current_progress = i * n_steps
        percent_cb(current_progress / total_number_of_steps * 100)
        if id not in REFERENCE_MAP:
            print(f"[WARNING] skipping {id} since it is not present in dataset", file=sys.stderr)
            continue
        entry = REFERENCE_MAP[id]
        print(f"[INFO] {id} info: {entry.metadata.repo} #PR {entry.metadata.pr_number}")
        try:
            build_handler = get_build_handler(
                ARCHIVES_ROOT, entry.metadata.archive_name(ArchiveState.MERGED)
            )
            current_progress += 1
            percent_cb(current_progress / total_number_of_steps * 100)
        except Exception as e:
            print(
                f"[ERROR] {id} ({entry.metadata.repo} #PR {entry.metadata.pr_number}) {type(e)}: {e}",
                file=sys.stderr,
            )
            continue

        build_handler.inject_changes(changes)
        current_progress += 1
        percent_cb(current_progress / total_number_of_steps * 100)

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
                    current_progress += 1
                    percent_cb(current_progress / total_number_of_steps * 100)
                except Exception as e:
                    results[id][task] = False
                    results[id][task + "_error_msg"] = str(e)
                    print(
                        f"[ERROR] {id} ({entry.metadata.repo} #PR {entry.metadata.pr_number}) {type(e)}: {e}",
                        file=sys.stderr,
                    )
                    break

        print(f"[INFO] Done with {id}...")

    complete_cb(results)
    return results
