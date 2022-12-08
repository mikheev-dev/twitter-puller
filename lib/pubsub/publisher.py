from abc import ABC, abstractmethod
from collections import deque
from logging import Logger

from lib.event import Event


class BasePublisher(ABC):
    @abstractmethod
    def publish(self, event: Event):
        raise NotImplementedError


class LogPublisher(BasePublisher):
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def publish(self, event: Event):
        self._logger.debug(event.body)


class SyncPublisher(LogPublisher):
    _q: deque

    def __init__(self, queue: deque, logger: Logger):
        self._q = queue
        super().__init__(logger)

    def publish(self, event: Event):
        super(SyncPublisher, self).publish(event)
        self._q.append(event)

    def clear(self):
        self._q.clear()
