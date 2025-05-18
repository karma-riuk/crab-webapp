from abc import ABC, abstractmethod
from enum import Enum
from threading import Thread
from typing import Callable, Iterable, Mapping, Optional, Set, Any


class Status(Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETE = "complete"


class Observer(ABC):
    @abstractmethod
    def updatePercentage(self, percentage: float):
        ...

    @abstractmethod
    def updateComplete(self, results: dict):
        ...


class SocketObserver(Observer):
    socket2obs: dict[str, "SocketObserver"] = {}

    def __init__(self, sid: str, socket_emit: Callable[[str, Any], None]) -> None:
        super().__init__()
        self.sid = sid
        self.socket_emit = socket_emit
        SocketObserver.socket2obs[self.sid] = self

    def updatePercentage(self, percentage: float):
        self.socket_emit("progress", {'percent': percentage})

    def updateComplete(self, results: dict):
        self.socket_emit("complete", results)
        SocketObserver.socket2obs.pop(self.sid)


class Subject:
    # TODO: maybe have a process or thread pool here to implement the queue
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

    def unregisterObserver(self, observer: Observer):
        self.observers.remove(observer)

    def notifyPercentage(self, percentage: float):
        self.percent = percentage
        for observer in self.observers:
            observer.updatePercentage(percentage)

    def notifyComplete(self, results: dict):
        self.status = Status.COMPLETE
        for observer in self.observers:
            observer.updateComplete({"type": self.type, "results": results})
        self.results = results
        # TODO: maybe save results to disk here?

    def launch_task(self, *args, **kwargs):
        self.status = Status.PROCESSING
        t = Thread(
            target=self.task,
            args=args,
            kwargs={
                **kwargs,
                "percent_cb": self.notifyPercentage,
                "complete_cb": self.notifyComplete,
            },
            daemon=True,
        )
        t.start()


request2status: dict[str, Subject] = {}
