from abc import ABC, abstractmethod
from logging import Logger

from lib.event import Event


class BasePublisher(ABC):
    @abstractmethod
    def publish(self, event: Event):
        raise NotImplementedError


class TestPublisher(BasePublisher):
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def publish(self, event: Event):
        self._logger.info(event.body)
