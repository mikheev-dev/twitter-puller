from abc import ABC, abstractmethod
from lib.event import Event


class BaseReceiver(ABC):
    @abstractmethod
    def receive(self) -> Event:
        raise NotImplementedError
