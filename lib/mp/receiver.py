from multiprocessing import Queue

from lib.event import Event
from lib.pubsub.receiver import BaseReceiver


class MPQueueReceiver(BaseReceiver):
    _q: Queue

    def __init__(self, queue: Queue):
        self._q = queue

    def receive(self) -> Event:
        return self._q.get()
