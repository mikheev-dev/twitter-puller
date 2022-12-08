from abc import ABC, abstractmethod
from collections import deque
from logging import Logger

from lib.event import Event


class BaseReceiver(ABC):
    @abstractmethod
    def receive(self) -> Event:
        raise NotImplementedError


class SyncReceiver(BaseReceiver):
    _log: Logger
    _q: deque

    def __init__(self, queue: deque, logger: Logger):
        self._q = queue
        self._log = logger
        super().__init__()

    def receive(self) -> Event:
        event = self._q.pop()
        self._log.debug(f"Got event {event}.")
        return event
