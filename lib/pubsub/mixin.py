from typing import Optional

from lib.pubsub.publisher import BasePublisher
from lib.pubsub.receiver import BaseReceiver


class PublisherMixin:
    _publisher: Optional[BasePublisher] = None

    def set_publisher(self, publisher: BasePublisher):
        self._publisher = publisher


class ReceiverMixin:
    _receiver: Optional[BaseReceiver] = None

    def set_receiver(self, receiver: BaseReceiver):
        self._receiver = receiver
