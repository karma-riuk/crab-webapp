from abc import ABC, abstractmethod
from enum import Enum
from threading import Thread
from typing import Callable, Optional, Set, Any


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
    uuid2subject: dict[str, "Subject"] = {}

    def __init__(self, id: str, type_: str, task: Callable) -> None:
        self.id = id
        self.type = type_
        self.observers: Set[Observer] = set()
        self.status: Status = Status.CREATED
        self.results: Optional[dict] = None
        self.task = task
        self.percent: float = -1

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
        # TODO: maybe save results to disk here?
