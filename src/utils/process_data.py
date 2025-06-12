import os
import sys
from typing_extensions import Callable
from utils.build_handlers import get_build_handler
from sacrebleu import sentence_bleu as bleu
from utils.dataset import ArchiveState, Comment, CommentGenSubmission, Dataset

REFERENCE_MAP = Dataset.from_json(os.environ["DATASET_PATH"]).build_reference_map()

ARCHIVES_ROOT = os.environ["ARCHIVES_ROOT"]


def comment_distance(submission: CommentGenSubmission, entry: Comment):
    if entry.from_ is None and entry.to is None:
        return "NA"
    if submission.line_from is None and submission.line_to is None:
        return "NA"

    # Collapse missing endpoints to the one defined endpoint
    # For entry:
    start1 = entry.from_ if entry.from_ is not None else entry.to
    end1 = entry.to if entry.to is not None else entry.from_
    # For submission:
    start2 = submission.line_from if submission.line_from is not None else submission.line_to
    end2 = submission.line_to if submission.line_to is not None else submission.line_from

    # Now both start1,end1 and start2,end2 are non-None
    # Normalize in case from > to (just in case):
    if start1 > end1:
        start1, end1 = end1, start1
    if start2 > end2:
        start2, end2 = end2, start2

    # Check for overlap
    if end1 >= start2 and end2 >= start1:
        return 0

    # Otherwise compute gap
    if end1 < start2:
        return start2 - end1
    else:  # end2 < start1
        return start1 - end2


def evaluate_comments(
    answers: dict[str, CommentGenSubmission],
    percent_cb: Callable[[float], None] = lambda _: None,
    complete_cb: Callable[[dict], None] = lambda _: None,
):
    # print("Started processing comments...")
    total = len(answers)
    results = {}
    for i, (id_, submission) in enumerate(answers.items(), 1):
        # print(f"[INFO] Processing {id_} ({i}/{total}: {i/total:.2%})...")
        if id_ not in REFERENCE_MAP:
            print(f"[WARNING] skipping {id} since it is not present in dataset", file=sys.stderr)
            continue
        entry = REFERENCE_MAP[id_]
        max_score = 0
        scores = []
        # print(f"[INFO] Processing paraphrases...")
        for p in [entry.comments[0].body] + entry.comments[0].paraphrases:
            score = round(bleu(submission.body, [p]).score, 2)
            scores.append(score)
            max_score = max(max_score, score)

        correct_file = submission.path == entry.comments[0].file
        # print(f"[INFO] Getting distance...")
        if correct_file:
            distance = comment_distance(submission, entry.comments[0])
        else:
            distance = "NA"

        # print(f"[INFO] Populating result...")
        results[id_] = {
            'max_bleu_score': max_score,
            'bleu_scores': scores,
            'proposed_comment': submission.__dict__,
            'correct_file': correct_file,
            'distance': distance,
        }
        percent_cb(int(i / total * 100))

    # print(f"[INFO] Sending results...")
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
        # print(f"[INFO] Processing {id} ({i}/{n_answers}: {i/n_answers:.2%})...")
        current_progress = i * n_steps
        percent_cb(current_progress / total_number_of_steps * 100)
        if id not in REFERENCE_MAP:
            print(f"[WARNING] skipping {id} since it is not present in dataset", file=sys.stderr)
            continue
        entry = REFERENCE_MAP[id]
        # print(f"[INFO] {id} info: {entry.metadata.repo} #PR {entry.metadata.pr_number}")
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

        results[id] = {}
        try:
            build_handler.inject_changes(changes)
        except Exception as e:
            results[id]["changes_injection"] = False
            results[id]["changes_injection_error_msg"] = str(e)
            print(
                f"[ERROR] {id} ({entry.metadata.repo} #PR {entry.metadata.pr_number}) {type(e)}: {e}",
                file=sys.stderr,
            )
            continue

        current_progress += 1
        percent_cb(current_progress / total_number_of_steps * 100)

        with build_handler:
            steps = [
                ("compilation", build_handler.compile_repo),
                ("test", build_handler.test_repo),
            ]
            for task, action in steps:
                try:
                    # print(f"[INFO] Executing {task}...")
                    action()
                    # print(f"[INFO] {task} executed successfully on {id}")
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

        # print(f"[INFO] Done with {id}...")

    complete_cb(results)
    return results
