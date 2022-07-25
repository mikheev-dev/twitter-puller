from abc import abstractmethod

from lib.config import BaseConfig
from lib.connectors.psql_connection import get_psql_connection
from lib.event import Event
from lib.pubsub.publisher import BasePublisher


class BasePostgresPublisher(BasePublisher):
    _cfg: BaseConfig
    _db_name: str

    _connection = None

    def __init__(self, cfg: BaseConfig, db_name: str):
        self._cfg = cfg
        self._db_name = db_name

    @abstractmethod
    def write_to_db(self, event: Event):
        raise NotImplementedError

    def publish(self, event: Event):
        if not self._connection:
            self._connection = get_psql_connection(self._cfg, self._db_name)
        self.write_to_db(event)