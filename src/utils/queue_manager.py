from concurrent.futures import ThreadPoolExecutor
from collections import deque
from utils.observer import Subject, Status


class QueueManager:
    """
    Manages a queue of Subjects, handling status transitions and allowing position queries:
      CREATED -> WAITING -> PROCESSING -> COMPLETE
    """

    def __init__(self, max_workers: int = 5) -> None:
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.wait_queue: deque[str] = deque()

    def submit(self, subject: Subject, *args, **kwargs) -> None:
        subject.status = Status.WAITING
        # Add to waiting queue
        self.wait_queue.append(subject.id)
        # Schedule the task on the executor
        self.executor.submit(self._run, subject, *args, **kwargs)

    def get_position(self, subject_id: str) -> int:
        """
        Returns 1-based position in waiting queue, or 0 if not waiting.
        """
        try:
            # index returns 0-based, so +1
            return self.wait_queue.index(subject_id) + 1
        except ValueError:
            return 0

    def _run(self, subject: Subject, *args, **kwargs) -> None:
        # Remove from waiting queue as it's now processing
        try:
            self.wait_queue.remove(subject.id)
        except ValueError:
            pass
        subject.status = Status.PROCESSING
        # Execute the user-defined task synchronously in this worker thread
        subject.task(
            *args,
            percent_cb=subject.notifyPercentage,
            complete_cb=subject.notifyComplete,
            **kwargs,
        )
