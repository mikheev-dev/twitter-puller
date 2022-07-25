from multiprocessing import Queue

from lib.event import Event
from lib.pubsub.publisher import BasePublisher


class MPQueuePublisher(BasePublisher):
    _q: Queue

    def __init__(self, queue: Queue):
        self._q = queue

    def publish(self, event: Event):
        self._q.put(event)
