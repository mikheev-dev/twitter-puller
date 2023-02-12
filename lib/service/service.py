from abc import ABC, abstractmethod
from logging import Logger

from lib.event import Event
from lib.pubsub.mixin import PublisherMixin, ReceiverMixin
from lib.pubsub.receiver import BaseReceiver
from lib.pubsub.publisher import BasePublisher


class BaseService(ABC):
    _logger: Logger
    _service_name: str
    _sync: bool

    def __init__(self, sync: bool = False):
        self._service_name = self.__class__.__name__
        self._sync = sync

    def setup(self):
        pass

    @abstractmethod
    def main(self):
        raise NotImplementedError

    def sync(self):
        pass

    def run(self):
        self.setup()
        try:
            while True:
                self.main()
        except Exception as e:
            self._logger.error(f"Exception {e}'s happened! {self._service_name} stopped.")


class PipelineService(BaseService, PublisherMixin, ReceiverMixin):
    def __init__(
            self,
            receiver: BaseReceiver,
            publisher: BasePublisher,
            logger: Logger,
            sync: bool = False,
    ):
        self._logger = logger
        BaseService.__init__(self, sync)
        self.set_receiver(receiver)
        self.set_publisher(publisher)

    def handle_event(self, event: Event) -> Event:
        return event

    def main(self):
        event = self._receiver.receive()
        self._logger.debug(f"{self._service_name}: Receive event.")
        event = self.handle_event(event)
        self._publisher.publish(event)
        self._logger.debug(f"{self._service_name}: Publish event.")

    def sync(self):
        count_read = 0
        try:
            while True:
                self.main()
                count_read += 1
        except Exception as e:
            print(f"Handled {count_read} events by {self.__class__.__name__}")
            return
