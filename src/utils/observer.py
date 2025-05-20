from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
import os, tempfile, threading, json
from typing import Callable, Optional, Set

RESULTS_DIR = os.getenv("RESULTS_DIR", "submission_results")


class Status(Enum):
    CREATED = "created"
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETE = "complete"


class Observer(ABC):
    @abstractmethod
    def updateStarted(self):
        ...

    @abstractmethod
    def updatePercentage(self, percentage: float):
        ...

    @abstractmethod
    def updateComplete(self, results: dict):
        ...


class SocketObserver(Observer):
    socket2obs: dict[str, "SocketObserver"] = {}

    def __init__(self, sid: str, socket_emit: Callable) -> None:
        super().__init__()
        self.sid = sid
        self.socket_emit = socket_emit
        SocketObserver.socket2obs[self.sid] = self

    def updateStarted(self):
        self.socket_emit("started-processing")

    def updatePercentage(self, percentage: float):
        self.socket_emit("progress", {'percent': percentage})

    def updateComplete(self, results: dict):
        self.socket_emit("complete", results)
        SocketObserver.socket2obs.pop(self.sid)


class Subject:
    obs2subject: dict[Observer, "Subject"] = {}
    id2subject: dict[str, "Subject"] = {}

    @classmethod
    def setup(cls):
        if not os.path.exists(RESULTS_DIR):
            os.mkdir(RESULTS_DIR)

        for file in os.listdir(RESULTS_DIR):
            file_path = os.path.join(RESULTS_DIR, file)
            if os.path.getsize(file_path) == 0:
                # submission was still being processed before the server stopped
                # the file was created but never written to, therefore must be removed
                os.remove(file_path)
                continue

            _, type_, _ = file.split("_")
            with open(file_path, "r") as f:
                subject = Subject(
                    type_, lambda: None, id=file, status=Status.COMPLETE, results=json.load(f)
                )
                cls.id2subject[file] = subject
                # calculate one week from the file's creation time
                creation_time = os.path.getctime(file_path)
                created_dt = datetime.fromtimestamp(creation_time)
                one_week_later = created_dt + timedelta(weeks=1)
                if one_week_later < datetime.now():
                    # file is older than one week, remove it
                    os.remove(file_path)
                else:
                    timer = threading.Timer(
                        (one_week_later - datetime.now()).total_seconds(), subject._rm_results_file
                    )
                    timer.daemon = True
                    timer.start()

    def __init__(
        self,
        type_: str,
        task: Callable,
        id: Optional[str] = None,
        status: Status = Status.CREATED,
        results: Optional[dict] = None,
    ) -> None:
        self.type = type_
        self.observers: Set[Observer] = set()
        self.status: Status = status
        self.results: Optional[dict] = results
        self.task = task
        self.percent: float = -1
        if id is None:
            _, self.full_path = tempfile.mkstemp(
                prefix=f"crab_{type_}_", dir=RESULTS_DIR, text=True
            )
            self.id = os.path.basename(self.full_path)
        else:
            self.full_path = os.path.abspath(os.path.join(RESULTS_DIR, id))
            self.id = id

    def registerObserver(self, observer: Observer) -> None:
        self.observers.add(observer)
        Subject.obs2subject[observer] = self

    def unregisterObserver(self, observer: Observer):
        self.observers.remove(observer)
        Subject.obs2subject.pop(observer)

    def notifyStarted(self):
        self.status = Status.PROCESSING
        for observer in self.observers:
            observer.updateStarted

    def notifyPercentage(self, percentage: float):
        self.percent = percentage
        for observer in self.observers:
            observer.updatePercentage(percentage)

    def notifyComplete(self, results: dict):
        self.status = Status.COMPLETE
        for observer in self.observers:
            observer.updateComplete({"type": self.type, "results": results})
            Subject.obs2subject.pop(observer)
        self.observers.clear()
        self.results = results
        with open(self.full_path, "w") as f:
            json.dump(results, f)
        delay_seconds = timedelta(weeks=1).total_seconds()

        timer = threading.Timer(delay_seconds, self._rm_results_file)
        timer.daemon = True
        timer.start()

    def _rm_results_file(self):
        if os.path.exists(self.full_path):
            os.remove(self.full_path)
